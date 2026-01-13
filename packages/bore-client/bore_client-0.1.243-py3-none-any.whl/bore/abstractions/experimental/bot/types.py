import json
import mimetypes
from typing import Any, Optional, Union
from uuid import uuid4

from ....clients.bot import (
    BotServiceStub,
    PushBotEventBlockingRequest,
    PushBotEventBlockingResponse,
    PushBotEventRequest,
)
from ....runner.common import FunctionContext
from .bot import BotEvent, BotEventType

BOT_VOLUME_NAME = "beta9-bot-inputs"


class BotContext(FunctionContext):
    session_id: str = ""
    transition_name: str = ""
    bot_stub: Optional[BotServiceStub] = None

    @classmethod
    def new(
        cls,
        *,
        config: Any,
        task_id: Optional[str],
        on_start_value: Optional[Any] = None,
        session_id: str = "",
        transition_name: str = "",
        bot_stub: Optional[BotServiceStub] = None,
    ) -> "BotContext":
        """
        Create a new instance of BotContext, to be passed directly into a bot transition handler
        """

        instance = cls(
            container_id=config.container_id,
            stub_id=config.stub_id or "",
            stub_type=config.stub_type,
            callback_url=config.callback_url,
            python_version=config.python_version,
            task_id=task_id,
            bind_port=config.bind_port,
            timeout=config.timeout,
            on_start_value=on_start_value,
        )

        instance.session_id = session_id
        instance.transition_name = transition_name
        instance.bot_stub = bot_stub
        return instance

    def push_event(self, *, event_type: BotEventType, event_value: str):
        """Send an event to the bot (supports all event types)"""

        print(f"Sending bot event<{event_type}> {event_value}")
        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        self.bot_stub.push_bot_event(
            PushBotEventRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=event_type,
                event_value=event_value,
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
            )
        )

    def prompt(
        self, msg: str, timeout_seconds: int = 10, wait_for_response=True
    ) -> Union[BotEvent, None]:
        """Send a raw prompt to your model. By default, this will wait for a response for up to timeout_seconds."""

        if not wait_for_response:
            if self.bot_stub is None:
                raise ValueError("bot_stub is required to push events")

            self.bot_stub.push_bot_event(
                PushBotEventRequest(
                    stub_id=self.stub_id or "",
                    session_id=self.session_id or "",
                    event_type=BotEventType.TRANSITION_MESSAGE,
                    event_value=msg,
                    metadata={
                        "task_id": self.task_id or "",
                        "session_id": self.session_id or "",
                        "transition_name": self.transition_name or "",
                    },
                )
            )
            return None

        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        r: PushBotEventBlockingResponse = self.bot_stub.push_bot_event_blocking(
            PushBotEventBlockingRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=BotEventType.TRANSITION_MESSAGE,
                event_value=msg,
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
                timeout_seconds=timeout_seconds,
            )
        )

        if not r.ok:
            return None

        return BotEvent(
            type=r.event.type,
            value=r.event.value,
            metadata=r.event.metadata,
        )

    def say(self, msg: str):
        """Send a message to the user from the bot"""

        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        self.bot_stub.push_bot_event(
            PushBotEventRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=BotEventType.AGENT_MESSAGE,
                event_value=msg,
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
            )
        )

    def confirm(self, *, description: str, timeout_seconds: int = 120) -> bool:
        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        r: PushBotEventBlockingResponse = self.bot_stub.push_bot_event_blocking(
            PushBotEventBlockingRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=BotEventType.CONFIRM_REQUEST,
                event_value=json.dumps(
                    {
                        "description": description,
                        "timeout_seconds": str(timeout_seconds),
                    }
                ),
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
                timeout_seconds=timeout_seconds,
            )
        )
        if not r.ok:
            return False

        return r.event.value == "true"

    def remember(self, obj: Any):
        """Store an arbitrary object in the bot's memory (must be JSON serializable)"""

        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        self.bot_stub.push_bot_event(
            PushBotEventRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=BotEventType.MEMORY_MESSAGE,
                event_value=json.dumps(obj),
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
            )
        )

    def send_file(self, *, path: str, description: str):
        """Capture a file and send it to the user"""

        from bore import Output

        o = Output(path=path)
        o.save()

        filetype, _ = mimetypes.guess_type(path)
        file_msg = {
            "url": o.public_url(),
            "description": description,
            "filetype": filetype,
        }

        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        self.bot_stub.push_bot_event(
            PushBotEventRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=BotEventType.OUTPUT_FILE,
                event_value=json.dumps(file_msg),
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
            )
        )

    def get_file(
        self, *, description: str, timeout_seconds: Optional[int] = -1
    ) -> Union[str, None]:
        """
        Request a file from the user.

        Args:
            description (str): Description of the requested file to be displayed to the user.
            timeout_seconds (int): Time to wait for the file in seconds. -1 for no timeout.

        Returns:
            str or None: Path to the file in the container.
        """

        file_id = uuid4().hex
        if self.bot_stub is None:
            raise ValueError("bot_stub is required to push events")

        r: PushBotEventBlockingResponse = self.bot_stub.push_bot_event_blocking(
            PushBotEventBlockingRequest(
                stub_id=self.stub_id or "",
                session_id=self.session_id or "",
                event_type=BotEventType.INPUT_FILE_REQUEST,
                event_value=json.dumps(
                    {
                        "description": description,
                        "file_id": file_id,
                        "timeout_seconds": str(timeout_seconds),
                        "volume_path": f"{BOT_VOLUME_NAME}/{self.session_id}/{file_id}",
                    }
                ),
                metadata={
                    "task_id": self.task_id or "",
                    "session_id": self.session_id or "",
                    "transition_name": self.transition_name or "",
                },
                timeout_seconds=timeout_seconds,
            )
        )
        if not r.ok:
            return None

        return r.event.value
