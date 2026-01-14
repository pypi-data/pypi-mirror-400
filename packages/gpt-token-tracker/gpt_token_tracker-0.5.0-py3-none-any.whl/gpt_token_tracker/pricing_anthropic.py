from anthropic.types import Usage
from .models import AnthropicModel
from .pricing import BasePricing, TOKENS_PER_PRICE


class PricingAnthropic(BasePricing):
    def compute_costs(self, u: Usage, model: str) -> AnthropicModel:
        input_tokens = u.input_tokens
        output_tokens = u.output_tokens

        cache_creation_tokens = u.cache_creation_input_tokens or 0
        cache_creation1h_tokens = getattr(u.cache_creation, "ephemeral_1h_input_tokens", 0)
        cache_creation5m_tokens = getattr(u.cache_creation, "ephemeral_5m_input_tokens", 0)
        cache_read_input_tokens = u.cache_read_input_tokens or 0

        pricing = self.pricing[model]

        input_cost = (
                                  input_tokens * pricing.get("all_in", 0)
                          ) / TOKENS_PER_PRICE

        cached_input_cost = (
                                   cache_read_input_tokens * pricing.get("cached_hit", 0)
                           ) / TOKENS_PER_PRICE

        cache_1h_cost = (
                                 cache_creation1h_tokens * pricing.get("cached_1h", 0)
                         ) / TOKENS_PER_PRICE

        cache_5m_cost = (
                                      cache_creation5m_tokens * pricing.get("cached_5m", 0)
                              ) / TOKENS_PER_PRICE

        output_cost = (
                                   output_tokens * pricing.get("all_out", 0)
                           ) / TOKENS_PER_PRICE

        total_cost = input_cost + cached_input_cost + cache_1h_cost + cache_5m_cost + output_cost

        return AnthropicModel(
            input_tokens=input_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_input_tokens=cache_read_input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=input_cost,
            cached_input_cost=cached_input_cost,
            cache_5m_cost=cache_5m_cost,
            cache_1h_cost=cache_1h_cost,
            output_cost=output_cost,
            total_cost=total_cost,
        )
