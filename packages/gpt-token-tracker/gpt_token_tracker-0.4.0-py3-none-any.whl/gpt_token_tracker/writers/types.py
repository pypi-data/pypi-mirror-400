from pathlib import Path
from pydantic import BaseModel
from google.genai.types import UsageMetadata
from anthropic.types import Usage
from typing import Protocol
from openai.types.responses.response_usage import ResponseUsage
from openai.types.realtime.realtime_response_usage import RealtimeResponseUsage
from openai.types.realtime.conversation_item_input_audio_transcription_completed_event import UsageTranscriptTextUsageTokens
from gpt_token_tracker.models import Timed


UsageTypes = ResponseUsage | RealtimeResponseUsage | UsageTranscriptTextUsageTokens | UsageMetadata | Usage | Timed


class Writer(Protocol):
    """Writers must accept a str name or file path."""
    def __init__(self, name: str | Path): ...

    def initialize(self, pricing: dict[str, dict[str, float]]) -> None: ...

    def write(self, model: str, result: str, usage: UsageTypes, costs: BaseModel, timed: bool = False): ...

    def close(self): ...

