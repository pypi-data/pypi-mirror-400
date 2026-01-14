from openai.types.responses.response_usage import ResponseUsage
from openai.types.realtime.realtime_response_usage import RealtimeResponseUsage
from openai.types.realtime.conversation_item_input_audio_transcription_completed_event import UsageTranscriptTextUsageTokens
from .models import RealtimeModel, ChatCompletionModel, RealtimeTranscribeModel
from .writers.types import UsageTypes

from abc import ABC, abstractmethod


TOKENS_PER_PRICE = 1_000_000


class BasePricing(ABC):
    def __init__(self, pricing: dict[str, dict[str, float]]):
        self.pricing = pricing

    @abstractmethod
    def compute_costs(self, u: UsageTypes, model: str):
        raise NotImplementedError


class PricingRealtime(BasePricing):
    def compute_costs(self, u: RealtimeResponseUsage, model: str) -> RealtimeModel:
        # Token counts
        input_text_tokens = u.input_token_details.text_tokens
        input_audio_tokens = u.input_token_details.audio_tokens
        input_image_tokens = u.input_token_details.image_tokens

        cached_text_tokens = u.input_token_details.cached_tokens_details.text_tokens
        cached_audio_tokens = u.input_token_details.cached_tokens_details.audio_tokens
        cached_image_tokens = u.input_token_details.cached_tokens_details.image_tokens

        output_text_tokens = u.output_token_details.text_tokens
        output_audio_tokens = u.output_token_details.audio_tokens

        input_tokens = (
            input_text_tokens
            + input_audio_tokens
            + input_image_tokens
            + cached_text_tokens
            + cached_audio_tokens
            + cached_image_tokens
        )

        output_tokens = output_text_tokens + output_audio_tokens

        total_tokens = u.total_tokens

        pricing = self.pricing[model]

        # Costs
        input_text_cost = (input_text_tokens * pricing.get("text_in", 0)) / TOKENS_PER_PRICE
        input_audio_cost = (input_audio_tokens * pricing.get("audio_in", 0)) / TOKENS_PER_PRICE
        input_image_cost = (input_image_tokens * pricing.get("image_in", 0)) / TOKENS_PER_PRICE

        cached_text_cost = (cached_text_tokens * pricing.get("cached_text_in", 0)) / TOKENS_PER_PRICE
        cached_audio_cost = (cached_audio_tokens * pricing.get("cached_audio_in", 0)) / TOKENS_PER_PRICE
        cached_image_cost = (cached_image_tokens * pricing.get("cached_image_in", 0)) / TOKENS_PER_PRICE

        text_output_cost = (output_text_tokens * pricing.get("text_out", 0)) / TOKENS_PER_PRICE
        audio_output_cost = (output_audio_tokens * pricing.get("audio_out", 0)) / TOKENS_PER_PRICE

        total_input_cost = (
            input_text_cost
            + input_audio_cost
            + input_image_cost
            + cached_text_cost
            + cached_audio_cost
            + cached_image_cost
        )

        total_output_cost = text_output_cost + audio_output_cost
        total_cost = total_input_cost + total_output_cost

        return RealtimeModel(
            input_tokens=input_tokens,
            input_text_tokens=input_text_tokens,
            input_audio_tokens=input_audio_tokens,
            input_image_tokens=input_image_tokens,

            cached_text_tokens=cached_text_tokens,
            cached_audio_tokens=cached_audio_tokens,
            cached_image_tokens=cached_image_tokens,

            output_tokens=output_tokens,
            output_text_tokens=output_text_tokens,
            output_audio_tokens=output_audio_tokens,

            total_tokens=total_tokens,

            input_text_cost=input_text_cost,
            input_audio_cost=input_audio_cost,
            input_image_cost=input_image_cost,

            cached_text_cost=cached_text_cost,
            cached_audio_cost=cached_audio_cost,
            cached_image_cost=cached_image_cost,

            text_output_cost=text_output_cost,
            audio_output_cost=audio_output_cost,

            total_input_cost=total_input_cost,
            total_output_cost=total_output_cost,
            total_cost=total_cost,
        )


class PricingTextCompletion(BasePricing):
    def compute_costs(self, u: ResponseUsage, model: str) -> ChatCompletionModel:
        input_text_tokens = u.input_tokens
        cached_text_tokens = u.input_tokens_details.cached_tokens
        output_text_tokens = u.output_tokens

        total_tokens = u.total_tokens

        pricing = self.pricing[model]

        input_text_cost = (
            input_text_tokens * pricing.get("text_in", 0)
        ) / TOKENS_PER_PRICE

        cached_text_cost = (
            cached_text_tokens * pricing.get("cached_text_in", 0)
        ) / TOKENS_PER_PRICE

        output_text_cost = (
            output_text_tokens * pricing.get("text_out", 0)
        ) / TOKENS_PER_PRICE

        total_cost = input_text_cost + cached_text_cost + output_text_cost

        return ChatCompletionModel(
            input_text_tokens=input_text_tokens,
            cached_text_tokens=cached_text_tokens,
            output_text_tokens=output_text_tokens,
            total_tokens=total_tokens,
            input_text_cost=input_text_cost,
            cached_text_cost=cached_text_cost,
            output_text_cost=output_text_cost,
            total_cost=total_cost,
        )


class PricingAudioTranscription(BasePricing):
    def compute_costs(self, u: UsageTranscriptTextUsageTokens, model: str) -> RealtimeTranscribeModel:
        input_text_tokens = u.input_token_details.text_tokens
        input_audio_tokens = u.input_token_details.audio_tokens
        output_text_tokens = u.output_tokens
        total_tokens = u.total_tokens

        pricing = self.pricing[model]

        input_text_cost = (
            input_text_tokens * pricing.get("text_in", 0)
        ) / TOKENS_PER_PRICE

        input_audio_cost = (
            input_audio_tokens * pricing.get("audio_in", 0)
        ) / TOKENS_PER_PRICE

        output_text_cost = (
            output_text_tokens * pricing.get("text_out", 0)
        ) / TOKENS_PER_PRICE

        total_cost = input_text_cost + input_audio_cost + output_text_cost

        return RealtimeTranscribeModel(
            input_text_tokens=input_text_tokens,
            input_audio_tokens=input_audio_tokens,
            output_text_tokens=output_text_tokens,
            total_tokens=total_tokens,
            input_text_cost=input_text_cost,
            input_audio_cost=input_audio_cost,
            output_text_cost=output_text_cost,
            total_cost=total_cost,
        )
