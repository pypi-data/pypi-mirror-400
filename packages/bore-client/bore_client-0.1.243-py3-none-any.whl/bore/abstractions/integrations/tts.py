"""
TTS (Text-to-Speech) Base Module

This module provides the base TTS class and registry mechanism for
deploying text-to-speech services on Beta9.

For specific engine implementations, see:
- tts_indextts.py: IndexTTS with vLLM backend
"""

import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from ... import terminal
from ...abstractions.base.container import Container
from ...abstractions.base.runner import ASGI_DEPLOYMENT_STUB_TYPE, ASGI_SERVE_STUB_TYPE
from ...abstractions.endpoint import ASGI
from ...abstractions.image import Image
from ...abstractions.volume import CloudBucket, Volume
from ...channel import with_grpc_error_handling
from ...clients.endpoint import StartEndpointServeRequest, StartEndpointServeResponse
from ...clients.gateway import DeployStubRequest, DeployStubResponse
from ...config import ConfigContext
from ...type import Autoscaler, GpuType, GpuTypeAlias, QueueDepthAutoscaler

# =============================================================================
# TTS Engine Registry
# =============================================================================

# Registry for built-in TTS engine classes
_TTS_ENGINE_REGISTRY: Dict[str, Type["TTS"]] = {}


def register_tts_engine(name: str) -> Callable[[Type["TTS"]], Type["TTS"]]:
    """
    Decorator to register a TTS engine class.

    Example:
        @register_tts_engine("IndexTTS")
        class IndexTTS(TTS):
            ...
    """

    def decorator(cls: Type["TTS"]) -> Type["TTS"]:
        _TTS_ENGINE_REGISTRY[name.lower()] = cls
        return cls

    return decorator


def get_registered_engines() -> List[str]:
    """Get list of registered TTS engine names."""
    return list(_TTS_ENGINE_REGISTRY.keys())


# =============================================================================
# Type Aliases
# =============================================================================

# Type alias for TTS engine factory
# Factory should return (tts_engine, speakers_dict)
TTSEngineFactory = Callable[[], Tuple[Any, Dict[str, Any]]]

# Type alias for inference function (supports both sync and async)
# (engine, voice, text) -> (sample_rate, wav_data) or Coroutine
TTSInferFunc = Callable[..., Any]


# =============================================================================
# TTS Base Class
# =============================================================================


class TTS(ASGI):
    """
    TTS is a generic wrapper for text-to-speech engines, allowing deployment as an ASGI app
    with OpenAI-compatible /audio/speech and /audio/voices endpoints.

    This is a base class that supports multiple usage patterns:

    1. **Auto-select built-in engine**: Specify `model` parameter to use a registered engine
    2. **Custom factory functions**: Provide `engine_factory` and `infer_func`
    3. **Subclassing**: Create a subclass and override `create_engine()` and `infer()`

    Parameters:
        model (Optional[str]):
            Name of a registered TTS engine (e.g., "IndexTTS", "CosyVoice").
            If specified and no custom factory is provided, uses the built-in implementation.
            Use `TTS.list_engines()` to see available engines.
        cpu (Union[int, float, str]):
            The number of CPU cores allocated to the container. Default is 2.0.
        memory (Union[int, str]):
            The amount of memory allocated to the container. Default is "16Gi".
        gpu (GpuTypeAlias):
            GPU type. Default is GpuType.NoGPU.
        gpu_count (int):
            Number of GPUs. Default is 0.
        image (Image):
            Container image configuration. Should include TTS engine dependencies.
        workers (int):
            Number of worker processes. Default is 1.
        concurrent_requests (int):
            Maximum number of concurrent requests. Default is 1.
        keep_warm_seconds (int):
            Seconds to keep the container warm. Default is 300.
        max_pending_tasks (int):
            Maximum number of pending tasks. Default is 100.
        timeout (int):
            Request timeout in seconds. Default is 600.
        authorized (bool):
            Whether authorization is required. Default is True.
        name (Optional[str]):
            Service name.
        volumes (Optional[List[Union[Volume, CloudBucket]]]):
            List of mounted volumes.
        secrets (Optional[List[str]]):
            List of injected secrets (e.g., HF_TOKEN).
        autoscaler (Autoscaler):
            Autoscaling strategy.
        engine_factory (Optional[TTSEngineFactory]):
            Factory function that initializes and returns (tts_engine, speakers_dict).
        infer_func (Optional[TTSInferFunc]):
            Function to perform TTS inference: (engine, voice, text) -> (sample_rate, wav_data).

    Example:
        ```python
        from bore.integrations import TTS

        # Method 1: Use built-in engine by name
        tts = TTS(
            name="my-tts",
            model="IndexTTS",  # Auto-uses IndexTTS implementation
            gpu="RTX4090",
        )

        # Method 2: Custom factory functions
        tts = TTS(
            name="my-tts",
            engine_factory=my_factory,
            infer_func=my_infer,
        )

        # Deploy
        result, ok = tts.deploy()
        ```
    """

    def __new__(
        cls,
        model: Optional[str] = None,
        engine_factory: Optional[TTSEngineFactory] = None,
        infer_func: Optional[TTSInferFunc] = None,
        **kwargs: Any,
    ) -> "TTS":
        """
        Create a TTS instance. If a model name is specified and no custom factory
        is provided, automatically use the registered engine class.
        """
        # If custom factory/infer provided, use base TTS class
        if engine_factory is not None or infer_func is not None:
            instance: TTS = object.__new__(cls)
            return instance

        # If model specified and registered, use the registered class
        if model and model.lower() in _TTS_ENGINE_REGISTRY:
            engine_cls = _TTS_ENGINE_REGISTRY[model.lower()]
            instance = object.__new__(engine_cls)
            return instance

        # Otherwise use base TTS class
        instance = object.__new__(cls)
        return instance

    def __init__(
        self,
        model: Optional[str] = None,
        cpu: Union[int, float, str] = 2.0,
        memory: Union[int, str] = "16Gi",
        gpu: GpuTypeAlias = GpuType.NoGPU,
        gpu_count: int = 0,
        image: Image = Image(python_version="python3.11"),
        workers: int = 1,
        concurrent_requests: int = 1,
        keep_warm_seconds: int = 300,
        max_pending_tasks: int = 100,
        timeout: int = 600,
        authorized: bool = True,
        name: Optional[str] = None,
        volumes: Optional[List[Union[Volume, CloudBucket]]] = None,
        secrets: Optional[List[str]] = None,
        autoscaler: Autoscaler = QueueDepthAutoscaler(),
        engine_factory: Optional[TTSEngineFactory] = None,
        infer_func: Optional[TTSInferFunc] = None,
        **kwargs: Any,
    ):
        if volumes is None:
            volumes = []

        # Add basic TTS dependencies
        image = image.add_python_packages(
            [
                "fastapi",
                "uvicorn",
                "soundfile",
                "numpy",
            ]
        )

        super().__init__(
            cpu=cpu,
            memory=memory,
            gpu=gpu,
            gpu_count=gpu_count,
            image=image,
            workers=workers,
            concurrent_requests=concurrent_requests,
            keep_warm_seconds=keep_warm_seconds,
            max_pending_tasks=max_pending_tasks,
            timeout=timeout,
            authorized=authorized,
            name=name,
            volumes=volumes,
            secrets=secrets,
            autoscaler=autoscaler,
        )

        self._model = model
        self._engine_factory = engine_factory
        self._infer_func = infer_func

    @classmethod
    def list_engines(cls) -> List[str]:
        """List all registered TTS engine names."""
        return get_registered_engines()

    def __name__(self) -> str:  # type: ignore[override]
        return self.name or "tts"

    def set_handler(self, handler: str) -> None:
        self.handler = handler

    def func(self, *args: Any, **kwargs: Any) -> None:
        pass

    def create_engine(self) -> Tuple[Any, Dict[str, Any]]:
        """
        Create and return the TTS engine and speakers dict.
        Override this method in subclasses or provide engine_factory in __init__.

        Returns:
            Tuple of (tts_engine, speakers_dict)
        """
        if self._engine_factory:
            return self._engine_factory()
        raise NotImplementedError(
            f"Either provide engine_factory in __init__, set model to one of {self.list_engines()}, "
            "or override create_engine() in subclass"
        )

    async def infer(self, engine: Any, voice: str, text: str) -> Tuple[int, Any]:
        """
        Perform TTS inference.
        Override this method in subclasses or provide infer_func in __init__.

        Args:
            engine: The TTS engine instance
            voice: Voice/speaker name
            text: Text to synthesize

        Returns:
            Tuple of (sample_rate, wav_data as numpy array)
        """
        import asyncio

        if self._infer_func:
            result = self._infer_func(engine, voice, text)
            # Handle both sync and async functions
            if asyncio.iscoroutine(result):
                return await result
            return result  # type: ignore[return-value]
        raise NotImplementedError(
            f"Either provide infer_func in __init__, set model to one of {self.list_engines()}, "
            "or override infer() in subclass"
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Called when the container starts, creates a FastAPI application with TTS endpoints.
        """
        import io
        import traceback

        import numpy as np
        import soundfile as sf  # type: ignore[import-not-found]
        from fastapi import FastAPI, Request, Response
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse

        # Create FastAPI application
        app = FastAPI(title="Beta9 TTS Service")

        # Add CORS support
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize TTS engine
        tts_engine: Any = None
        speakers_dict: Dict[str, Any] = {}

        @app.on_event("startup")
        async def startup() -> None:
            nonlocal tts_engine, speakers_dict
            tts_engine, speakers_dict = self.create_engine()

        # ==================== Health Check ====================
        @app.get("/health")
        async def health_check() -> Any:
            if tts_engine is None:
                return JSONResponse(
                    status_code=503,
                    content={"status": "unhealthy", "message": "TTS engine not initialized"},
                )
            return {"status": "healthy"}

        # ==================== OpenAI Compatible API ====================
        @app.post("/audio/speech")
        async def create_speech(request: Request) -> Any:
            """
            OpenAI-compatible text-to-speech API.

            Request format:
            {
                "model": "tts-1",           // Model name (for compatibility)
                "input": "Text content",     // Required
                "voice": "alloy",           // Voice name
                "response_format": "wav",   // Optional: wav, mp3, etc.
            }
            """
            try:
                data = await request.json()
                text = data.get("input")
                voice = data.get("voice")
                response_format = data.get("response_format", "wav")

                # Parameter validation
                if not text:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": {
                                "message": "Missing required parameter: 'input'",
                                "type": "invalid_request_error",
                                "code": "missing_required_parameter",
                            }
                        },
                    )

                if len(text) > 4096:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": {
                                "message": f"Input text too long: {len(text)} > 4096 characters",
                                "type": "invalid_request_error",
                                "code": "input_too_long",
                            }
                        },
                    )

                if not voice or voice not in speakers_dict:
                    available = list(speakers_dict.keys())
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": {
                                "message": f"Invalid voice '{voice}'. Available: {available}",
                                "type": "invalid_request_error",
                                "code": "invalid_voice",
                            }
                        },
                    )

                # Content-Type mapping
                content_type_map = {
                    "mp3": "audio/mpeg",
                    "opus": "audio/opus",
                    "aac": "audio/aac",
                    "flac": "audio/flac",
                    "wav": "audio/wav",
                    "pcm": "audio/pcm",
                }
                content_type = content_type_map.get(response_format, "audio/wav")

                # Perform inference
                sr, wav = await self.infer(tts_engine, voice, text)

                # Encode audio
                with io.BytesIO() as buffer:
                    if response_format == "pcm":
                        buffer.write(wav.astype(np.int16).tobytes())
                    else:
                        sf.write(buffer, wav, sr, format=response_format.upper())
                    audio_bytes = buffer.getvalue()

                return Response(content=audio_bytes, media_type=content_type)

            except Exception as ex:
                traceback.format_exc()
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "message": str(ex),
                            "type": "internal_error",
                            "code": "internal_error",
                        }
                    },
                )

        @app.get("/audio/voices")
        async def list_voices() -> Any:
            """Get list of available voices."""
            voices = []
            for voice_id in speakers_dict.keys():
                voices.append(
                    {
                        "voice_id": voice_id,
                        "name": voice_id.capitalize(),
                        "preview_url": None,
                        "description": f"Voice: {voice_id}",
                    }
                )
            return {"voices": voices}

        # ==================== Native TTS API ====================
        @app.post("/tts")
        async def tts_api(request: Request) -> Any:
            """
            Native TTS API.

            Request format:
            {
                "text": "Text content",
                "voice": "Voice name"
            }
            """
            try:
                data = await request.json()
                text = data["text"]
                voice = data["voice"]

                sr, wav = await self.infer(tts_engine, voice, text)

                with io.BytesIO() as wav_buffer:
                    sf.write(wav_buffer, wav, sr, format="WAV")
                    wav_bytes = wav_buffer.getvalue()

                return Response(content=wav_bytes, media_type="audio/wav")

            except Exception:
                tb_str = traceback.format_exc()
                return JSONResponse(
                    status_code=500, content={"status": "error", "error": str(tb_str)}
                )

        return app

    def deploy(
        self,
        name: Optional[str] = None,
        context: Optional[ConfigContext] = None,
        invocation_details_func: Optional[Callable[..., None]] = None,
        **invocation_details_options: Any,
    ) -> Tuple[Dict[str, Any], bool]:
        """Deploy TTS service"""
        self.name = name or self.name
        if not self.name:
            terminal.error(
                "You must specify an app name (either in the decorator or via the --name argument)."
            )
            return {}, False

        if context is not None:
            self.config_context = context

        if not self.prepare_runtime(
            stub_type=ASGI_DEPLOYMENT_STUB_TYPE,
            force_create_stub=True,
        ):
            return {}, False

        terminal.header("Deploying TTS Service")
        deploy_response: DeployStubResponse = self.gateway_stub.deploy_stub(
            DeployStubRequest(stub_id=self.stub_id, name=self.name)
        )

        self.deployment_id = deploy_response.deployment_id
        if deploy_response.ok:
            terminal.header("Deployed TTS Service 🎉")
            if invocation_details_func:
                invocation_details_func(**invocation_details_options)
            else:
                self.print_invocation_snippet(**invocation_details_options)

        return {
            "deployment_id": deploy_response.deployment_id,
        }, deploy_response.ok

    @with_grpc_error_handling
    def serve(self, timeout: int = 0, url_type: str = "") -> Any:
        """Local debug mode"""
        stub_type = ASGI_SERVE_STUB_TYPE

        if not self.prepare_runtime(func=self.func, stub_type=stub_type, force_create_stub=True):
            return False

        try:
            with terminal.progress("Serving TTS endpoint..."):
                self.print_invocation_snippet(url_type=url_type)
                return self._serve(dir=os.getcwd(), timeout=timeout)
        except KeyboardInterrupt:
            terminal.header("Stopping serve container")
            terminal.print("Goodbye 👋")
            os._exit(0)

    def _serve(self, *, dir: str, timeout: int = 0) -> Any:
        r: StartEndpointServeResponse = self.endpoint_stub.start_endpoint_serve(
            StartEndpointServeRequest(
                stub_id=self.stub_id,
                timeout=timeout,
            )
        )
        if not r.ok:
            return terminal.error(r.error_msg)

        container = Container(container_id=r.container_id)
        container.attach(container_id=r.container_id, sync_dir=dir)


# =============================================================================
# Import built-in engines to register them
# =============================================================================

# Import IndexTTS to trigger registration via @register_tts_engine decorator
from . import tts_indextts as _  # noqa: F401, E402
