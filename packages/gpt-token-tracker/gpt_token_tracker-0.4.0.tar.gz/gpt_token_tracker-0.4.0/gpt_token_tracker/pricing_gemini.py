from  google.genai.types import UsageMetadata
from .pricing import BasePricing
from .models import GeminiModel



TOKENS_PER_PRICE = 1_000_000


class PricingGemini(BasePricing):
    def compute_costs(self, u: UsageMetadata, model: str) -> GeminiModel:
        # Token counts
        input_tokens = u.prompt_token_count
        input_token_details = u.prompt_tokens_details
        input_audio_tokens = 0
        input_text_tokens = 0
        input_image_tokens = 0
        input_document_tokens = 0
        input_video_tokens = 0

        for m in input_token_details:
            if m.modality == "AUDIO":
                input_audio_tokens = m.token_count
            elif m.modality == "TEXT":
                input_text_tokens = m.token_count
            elif m.modality == "IMAGE":
                input_image_tokens = m.token_count
            elif m.modality == "DOCUMENT":
                input_document_tokens = m.token_count
            elif m.modality == "VIDEO":
                input_video_tokens = m.token_count

        cached_tokens = u.cached_content_token_count
        cached_token_details = u.cache_tokens_details
        cached_audio_tokens = 0
        cached_text_tokens = 0
        cached_image_tokens = 0
        cached_document_tokens = 0
        cached_video_tokens = 0

        for m in cached_token_details or []:
            if m.modality == "AUDIO":
                cached_audio_tokens = m.token_count
            elif m.modality == "TEXT":
                cached_text_tokens = m.token_count
            elif m.modality == "IMAGE":
                cached_image_tokens = m.token_count
            elif m.modality == "DOCUMENT":
                cached_document_tokens = m.token_count
            elif m.modality == "VIDEO":
                cached_video_tokens = m.token_count

        output_tokens = u.response_token_count
        output_token_details = u.response_tokens_details
        output_audio_tokens = 0
        output_text_tokens = 0
        output_image_tokens = 0
        output_document_tokens = 0
        output_video_tokens = 0

        for m in output_token_details:
            if m.modality == "AUDIO":
                output_audio_tokens = m.token_count
            elif m.modality == "TEXT":
                output_text_tokens = m.token_count
            elif m.modality == "IMAGE":
                output_image_tokens = m.token_count
            elif m.modality == "DOCUMENT":
                output_document_tokens = m.token_count
            elif m.modality == "VIDEO":
                output_video_tokens = m.token_count

        thinking_tokens = u.thoughts_token_count
        total_tokens = input_tokens + output_tokens + thinking_tokens

        pricing = self.pricing[model]

        # Costs
        input_text_cost = (input_text_tokens * pricing.get("text_in", 0)) / TOKENS_PER_PRICE
        input_audio_cost = (input_audio_tokens * pricing.get("audio_in", 0)) / TOKENS_PER_PRICE
        input_image_cost = (input_image_tokens * pricing.get("image_in", 0)) / TOKENS_PER_PRICE
        input_video_cost = (input_video_tokens * pricing.get("video_in", 0)) / TOKENS_PER_PRICE
        input_document_cost = (input_document_tokens * pricing.get("document_in", 0)) / TOKENS_PER_PRICE

        cached_text_cost = (cached_text_tokens * pricing.get("cached_text_in", 0)) / TOKENS_PER_PRICE
        cached_audio_cost = (cached_audio_tokens * pricing.get("cached_audio_in", 0)) / TOKENS_PER_PRICE
        cached_image_cost = (cached_image_tokens * pricing.get("cached_image_in", 0)) / TOKENS_PER_PRICE
        cached_video_cost = (cached_video_tokens * pricing.get("cached_video_in", 0)) / TOKENS_PER_PRICE
        cached_document_cost = (cached_document_tokens * pricing.get("cached_document_in", 0)) / TOKENS_PER_PRICE

        output_text_cost = (output_text_tokens * pricing.get("text_out", 0)) / TOKENS_PER_PRICE
        output_audio_cost = (output_audio_tokens * pricing.get("audio_out", 0)) / TOKENS_PER_PRICE
        output_image_cost = (output_image_tokens * pricing.get("image_out", 0)) / TOKENS_PER_PRICE
        output_video_cost = (output_video_tokens * pricing.get("video_out", 0)) / TOKENS_PER_PRICE
        output_document_cost = (output_document_tokens * pricing.get("document_out", 0)) / TOKENS_PER_PRICE

        thinking_cost = (thinking_tokens * pricing.get("thinking", 0)) / TOKENS_PER_PRICE

        total_input_cost = (
            input_text_cost
            + input_audio_cost
            + input_image_cost
            + input_video_cost
            + input_document_cost
            + cached_text_cost
            + cached_audio_cost
            + cached_image_cost
            + cached_video_cost
            + cached_document_cost
        )

        total_output_cost = output_text_cost + output_audio_cost + output_image_cost + output_video_cost + output_document_cost
        total_cost = total_input_cost + total_output_cost + thinking_cost

        return GeminiModel(
            input_tokens=input_tokens,
            input_text_tokens=input_text_tokens,
            input_audio_tokens=input_audio_tokens,
            input_image_tokens=input_image_tokens,
            input_video_tokens=input_video_tokens,
            input_document_tokens=input_document_tokens,

            cached_text_tokens=cached_text_tokens,
            cached_audio_tokens=cached_audio_tokens,
            cached_image_tokens=cached_image_tokens,
            cached_video_tokens=cached_video_tokens,
            cached_document_tokens=cached_document_tokens,

            output_tokens=output_tokens,
            output_text_tokens=output_text_tokens,
            output_audio_tokens=output_audio_tokens,
            output_image_tokens=output_image_tokens,
            output_video_tokens=output_video_tokens,
            output_document_tokens=output_document_tokens,

            thinking_tokens=thinking_tokens,
            total_tokens=total_tokens,

            input_text_cost=input_text_cost,
            input_audio_cost=input_audio_cost,
            input_image_cost=input_image_cost,
            input_video_cost=input_video_cost,
            input_document_cost=input_document_cost,

            cached_text_cost=cached_text_cost,
            cached_audio_cost=cached_audio_cost,
            cached_image_cost=cached_image_cost,
            cached_video_cost=cached_video_cost,
            cached_document_cost=cached_document_cost,

            text_output_cost=output_text_cost,
            audio_output_cost=output_audio_cost,
            image_output_cost=output_image_cost,
            video_output_cost=output_video_cost,
            document_output_cost=output_document_cost,

            total_input_cost=total_input_cost,
            total_output_cost=total_output_cost,
            thinking_cost=thinking_cost,
            total_cost=total_cost,
        )
