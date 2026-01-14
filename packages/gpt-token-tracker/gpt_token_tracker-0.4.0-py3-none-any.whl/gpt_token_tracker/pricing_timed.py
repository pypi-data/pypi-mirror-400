from .models import Timed, TimedIntervalModel
from .pricing import BasePricing

TIME_INTERVAL_SECONDS = 60


class PricingTimeInterval(BasePricing):
    def compute_costs(self, u: Timed, model: str) -> TimedIntervalModel:
        seconds = (u.end_time - u.start_time).total_seconds()

        pricing = self.pricing[model]

        # Costs
        total_cost = (seconds / TIME_INTERVAL_SECONDS * pricing.get("per_interval", 0))

        return TimedIntervalModel(
            start_time=u.start_time,
            end_time=u.end_time,
            minutes=seconds / 60,
            total_cost=total_cost,
        )
