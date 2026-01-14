from pydantic import BaseModel
from datetime import datetime
from .writers.types import Writer, UsageTypes
from .pricing import BasePricing


class TokenLogger:
    """Routes usage objects to the appropriate writer. Writers compute costs."""

    def __init__(
        self,
        writer: Writer,
        pricing: BasePricing,
    ):
        self.pricing = pricing
        self.writer = writer
        self.writer.initialize(pricing.pricing)

    def compute_costs(self, usage: UsageTypes, model: str):
        return self.pricing.compute_costs(usage, model)

    def log(self, model: str, result: str, usage: UsageTypes, costs: BaseModel):
        self.writer.write(model, result, usage, costs)

    def log_timed(self, model: str, usage: UsageTypes, costs: BaseModel):
        self.writer.write(model, "", usage, costs, timed=True)

    def record(self, model: str, result: str, usage: UsageTypes):
        costs = self.compute_costs(usage, model)
        self.log(model, result, usage, costs)

    def record_timed(self, model: str, usage: UsageTypes):
        costs = self.compute_costs(usage, model)
        self.log_timed(model, usage, costs)

    def close(self):
        self.writer.close()
