from pydantic import BaseModel
from typing import Any


def format_field(name: str) -> str:
    return name.replace("_", " ").title()

def get_fields_for_model(costs: BaseModel) -> dict[str, Any]:
    cost_parts = {}
    for field_name, value in costs.model_dump().items():
        label = format_field(field_name)
        if isinstance(value, float):
            cost_parts[label] = value
        else:
            cost_parts[label] = value
    return cost_parts


def normalise_result(result: str) -> str:
    if not isinstance(result, str):
        result = str(result)
    return result.replace("\r\n", "\\n").replace("\n", "\\n")
