import csv
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime
from .utils import get_fields_for_model, normalise_result
from .types import UsageTypes


def get_timestamp() -> str:
    return datetime.now().isoformat()


class CSVWriter:
    """CSV writer that logs usage and cost models in a structured format."""

    def __init__(self, name: str | Path):
        self.path = Path(name)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = self.path.exists()
        has_content = file_exists and self.path.stat().st_size > 0

        self._file = self.path.open("a", newline="")
        self._writer: csv.DictWriter | None = None
        self._header_written = has_content

    def initialize(self, pricing: dict[str, dict[str, float]]) -> None:
        # CSV does not need pricing, but keep API parity with other writers
        pass

    def write(
        self,
        model: str,
        result: str,
        usage: UsageTypes,
        costs: BaseModel,
        timed: bool = False
    ):
        row = {
            "Timestamp": get_timestamp(),
            "Model": model,
        }

        if not timed:
            row["Result"] = normalise_result(result)

        row.update(get_fields_for_model(costs))

        if self._writer is None:
            self._writer = csv.DictWriter(self._file, fieldnames=row.keys())

            if not self._header_written:
                self._writer.writeheader()
                self._header_written = True

        self._writer.writerow(row)
        self._file.flush()

    def close(self):
        if self._file:
            self._file.close()
            self._file = None
            self._writer = None
