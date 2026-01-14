from typing import Any
from sqlmodel import SQLModel


class FieldValidator:
    @staticmethod
    def validate_field_length(model: SQLModel, field_name: str, value: Any):
        if field_name in model.__fields__:
            field_info = model.__fields__[field_name]
            max_length = None
            if (
                hasattr(field_info.type_, "__origin__")
                and field_info.type_.__origin__ is str
            ):
                # Skip, cannot determine
                return
            if hasattr(field_info.type_, "__args__") and field_info.type_.__args__:
                max_length = getattr(field_info.type_, "length", None)
            if max_length and isinstance(value, str) and len(value) > max_length:
                raise ValueError(
                    f"Field '{field_name}' exceeds max length {max_length}"
                )
