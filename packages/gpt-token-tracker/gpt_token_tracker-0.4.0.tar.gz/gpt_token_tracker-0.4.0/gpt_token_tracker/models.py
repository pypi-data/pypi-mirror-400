import datetime

from pydantic import BaseModel


class RealtimeModel(BaseModel):
    input_tokens: int
    input_text_tokens: int
    input_audio_tokens: int
    input_image_tokens: int
    cached_text_tokens: int
    cached_audio_tokens: int
    cached_image_tokens: int
    output_tokens: int
    output_text_tokens: int
    output_audio_tokens: int
    total_tokens: int
    input_text_cost: float
    input_audio_cost: float
    input_image_cost: float
    cached_text_cost: float
    cached_audio_cost: float
    cached_image_cost: float
    text_output_cost: float
    audio_output_cost: float
    total_input_cost: float
    total_output_cost: float
    total_cost: float


class RealtimeTranscribeModel(BaseModel):
    input_text_tokens: int
    input_audio_tokens: int
    output_text_tokens: int
    total_tokens: int
    input_text_cost: float
    input_audio_cost: float
    output_text_cost: float
    total_cost: float


class ChatCompletionModel(BaseModel):
    input_text_tokens: int
    cached_text_tokens: int
    output_text_tokens: int
    total_tokens: int
    input_text_cost: float
    cached_text_cost: float
    output_text_cost: float
    total_cost: float


class GeminiModel(BaseModel):
    input_tokens: int
    input_text_tokens: int
    input_audio_tokens: int
    input_image_tokens: int
    input_video_tokens: int
    input_document_tokens: int
    cached_text_tokens: int
    cached_audio_tokens: int
    cached_image_tokens: int
    cached_video_tokens: int
    cached_document_tokens: int
    output_tokens: int
    output_text_tokens: int
    output_audio_tokens: int
    output_image_tokens: int
    output_video_tokens: int
    output_document_tokens: int
    thinking_tokens: int
    total_tokens: int
    input_text_cost: float
    input_audio_cost: float
    input_image_cost: float
    input_video_cost: float
    input_document_cost: float
    cached_text_cost: float
    cached_audio_cost: float
    cached_image_cost: float
    cached_video_cost: float
    cached_document_cost: float
    text_output_cost: float
    audio_output_cost: float
    image_output_cost: float
    video_output_cost: float
    document_output_cost: float
    total_input_cost: float
    total_output_cost: float
    thinking_cost: float
    total_cost: float

class AnthropicModel(BaseModel):
    input_tokens: int
    cache_creation_tokens: int
    cache_read_input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    cached_input_cost: float
    cache_5m_cost: float
    cache_1h_cost: float
    output_cost: float
    total_cost: float


class Timed(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime


class TimedIntervalModel(Timed):
    start_time: datetime.datetime
    end_time: datetime.datetime
    minutes: float
    total_cost: float
