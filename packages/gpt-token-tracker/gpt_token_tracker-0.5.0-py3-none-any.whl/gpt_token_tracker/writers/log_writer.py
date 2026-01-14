import logging
from pathlib import Path
from pydantic import BaseModel
from .types import UsageTypes
from .utils import get_fields_for_model, normalise_result


class LogWriter:
    """Log writer that logs to a Python logger and computes cost data."""

    def __init__(self, name: str | Path):
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            # Set up the logger format and console stream handler if not already set
            self.logger.setLevel(logging.INFO)
            log_format = (
                "%(asctime)s | %(message)s"
            )
            formatter = logging.Formatter(log_format)
            handler = logging.StreamHandler()  # You can change this to a FileHandler if needed
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def initialize(self, pricing: dict[str, dict[str, float]]) -> None: ...

    def write(
            self,
            model: str,
            result: str,
            usage: UsageTypes,
            costs: BaseModel,
            timed: bool = False
    ):

        cost_parts = []
        for label, value in get_fields_for_model(costs).items():
            if isinstance(value, float):
                cost_parts.append(f"{label}: {value:.6f}")
            else:
                cost_parts.append(f"{label}: {value}")

        if timed:
            log_message = (
                    f"Model: {model} | "
                    + " | ".join(cost_parts)
            )
        else:
            log_message = (
                f"Model: {model} | "
                f"Result: {normalise_result(result)} | "
                + " | ".join(cost_parts)
        )

        self.logger.info(log_message)

    def close(self):
        # No resources to close, logging just happens to the stream or file handler
        pass
