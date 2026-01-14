"""Internal utilities for parsing data into dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypeVar, cast, get_args, get_origin, get_type_hints

T = TypeVar("T")

# Import at runtime for get_type_hints to resolve forward references
from .models import TrackingData


@dataclass
class TrackingDataDict:
    """Internal wrapper for tracking data dictionary."""

    data: dict[str, TrackingData]


def dict_to_dataclass(cls: type[T], data: dict[str, Any]) -> T:
    """
    Convert a dictionary to a dataclass instance, recursively handling nested dataclasses.

    Args:
        cls: The dataclass type to create
        data: Dictionary containing the data

    Returns:
        An instance of the dataclass

    """
    if not is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")

    type_hints = get_type_hints(cls)

    field_values: dict[str, Any] = {}

    for field in fields(cls):
        if field.name not in data:
            # ! Skip missing fields if they have defaults
            continue

        value = data[field.name]
        field_type = type_hints.get(field.name, field.type)

        if value is None:
            field_values[field.name] = None
            continue

        origin = get_origin(field_type)
        if origin is dict:
            args = get_args(field_type)
            if len(args) == 2 and is_dataclass(args[1]):
                value_type = cast("type[Any]", args[1])
                field_values[field.name] = {k: dict_to_dataclass(value_type, v) for k, v in value.items()}
            else:
                field_values[field.name] = value

        elif is_dataclass(field_type) and isinstance(value, dict):
            field_values[field.name] = dict_to_dataclass(cast("type[Any]", field_type), value)

        else:
            field_values[field.name] = value

    return cls(**field_values)
