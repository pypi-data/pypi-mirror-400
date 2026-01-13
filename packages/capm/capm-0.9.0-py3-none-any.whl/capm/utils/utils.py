from dataclasses import asdict
from typing import Any


def data_class_to_dict(data_class: Any):
    def dict_factory(x: list[tuple[str, Any]]) -> dict: return {k: v for (k, v) in x if v is not None}

    return asdict(data_class, dict_factory=dict_factory)
