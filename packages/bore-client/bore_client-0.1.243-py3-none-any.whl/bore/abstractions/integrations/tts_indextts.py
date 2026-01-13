"""
IndexTTS Engine Implementation

This module provides the IndexTTS implementation using vLLM backend.
IndexTTS is a high-quality Chinese/English TTS model with voice cloning capabilities.

Usage:
    from bore.integrations import TTS, IndexTTS, IndexTTSConfig

    # Method 1: Auto-select via model name
    tts = TTS(model="IndexTTS", name="my-tts", gpu="RTX4090")

    # Method 2: Direct instantiation
    tts = IndexTTS(
        name="my-tts",
        gpu="RTX4090",
        config=IndexTTSConfig(
            model_dir="IndexTeam/Index-TTS",
            speakers={"alloy": ["ref.wav"]},
        ),
    )
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ...abstractions.image import Image
from .tts import TTS, register_tts_engine


@dataclass
class IndexTTSConfig:
    """Configuration for IndexTTS engine."""

    model_dir: str = "IndexTeam/Index-TTS"
    """Model directory or HuggingFace model ID"""

    is_fp16: bool = True
    """Whether to use FP16 precision (GPU only)"""

    gpu_memory_utilization: float = 0.25
    """GPU memory utilization ratio (0.0-1.0)"""

    use_cuda_kernel: Optional[bool] = None
    """Whether to use BigVGAN CUDA custom kernel (None=auto)"""

    speakers: Optional[Dict[str, List[str]]] = None
    """Pre-registered speaker configuration: {"speaker_name": ["ref_audio.wav", ...]}"""

    speakers_json_path: Optional[str] = None
    """Speaker configuration JSON file path"""


@register_tts_engine("IndexTTS")
class IndexTTS(TTS):
    """
    IndexTTS implementation using vLLM backend.

    IndexTTS is a high-quality Chinese/English TTS model with:
    - Voice cloning from reference audio
    - vLLM acceleration for fast inference
    - Support for multiple speakers

    Parameters:
        All parameters from TTS base class, plus:

        config (IndexTTSConfig):
            IndexTTS-specific configuration including model path,
            GPU settings, and speaker configurations.

    Example:
        ```python
        from bore.integrations import TTS, IndexTTS, IndexTTSConfig

        # Method 1: Auto-select by model name
        tts = TTS(
            name="my-indextts",
            model="IndexTTS",
            gpu="RTX4090",
        )

        # Method 2: Direct instantiation with config
        tts = IndexTTS(
            name="my-indextts",
            gpu="RTX4090",
            config=IndexTTSConfig(
                model_dir="IndexTeam/Index-TTS",
                gpu_memory_utilization=0.25,
                speakers={
                    "alloy": ["voices/alloy.wav"],
                    "echo": ["voices/echo.wav"],
                },
            ),
        )

        # Deploy
        result, ok = tts.deploy()
        ```
    """

    def __init__(
        self,
        config: Optional[IndexTTSConfig] = None,
        **kwargs: Any,
    ):
        # Get or create image
        image = kwargs.pop("image", Image(python_version="python3.11"))

        # Add IndexTTS-specific dependencies
        image = image.add_python_packages(
            [
                "vllm==0.10.2",
                "omegaconf",
                "sentencepiece",
                "modelscope",
                "munch==4.0.0",
                "loguru",
                "librosa",
                "descript-audiotools==0.7.2",
                "matplotlib==3.8.2",
            ]
        )
        image = image.add_commands(["pip install WeTextProcessing || pip install wetext"])

        # Remove model from kwargs if present (we handle it ourselves)
        kwargs.pop("model", None)

        super().__init__(image=image, **kwargs)

        self.config = config or IndexTTSConfig()

    def _register_vllm_model(self) -> None:
        """Register vLLM custom GPT2 TTS model"""
        try:
            from indextts.gpt.index_tts_gpt2_vllm_v1 import GPT2TTSModel  # type: ignore[import-not-found]
            from vllm import ModelRegistry  # type: ignore[import-not-found]

            ModelRegistry.register_model("GPT2InferenceModel", GPT2TTSModel)
        except ImportError:
            pass  # Model may already be registered

    def create_engine(self) -> Tuple[Any, Dict[str, Any]]:
        """Initialize IndexTTS engine"""
        import json

        # Register vLLM model first
        self._register_vllm_model()

        from indextts.infer_vllm import IndexTTS as IndexTTSEngine  # type: ignore[import-not-found]

        engine = IndexTTSEngine(
            model_dir=self.config.model_dir,
            is_fp16=self.config.is_fp16,
            gpu_memory_utilization=self.config.gpu_memory_utilization,
            use_cuda_kernel=self.config.use_cuda_kernel,
        )

        speakers_dict: Dict[str, Any] = {}

        # Register pre-configured speakers
        if self.config.speakers:
            for speaker, audio_paths in self.config.speakers.items():
                engine.registry_speaker(speaker, audio_paths)
                speakers_dict[speaker] = {"audio_paths": audio_paths}

        # Load speakers from JSON file
        if self.config.speakers_json_path and os.path.exists(self.config.speakers_json_path):
            with open(self.config.speakers_json_path, "r") as f:
                file_speakers = json.load(f)
            for speaker, audio_paths in file_speakers.items():
                engine.registry_speaker(speaker, audio_paths)
                speakers_dict[speaker] = {"audio_paths": audio_paths}

        return engine, speakers_dict

    async def infer(self, engine: Any, voice: str, text: str) -> Tuple[int, Any]:
        """Perform IndexTTS inference"""
        return await engine.infer_with_ref_audio_embed(voice, text)
