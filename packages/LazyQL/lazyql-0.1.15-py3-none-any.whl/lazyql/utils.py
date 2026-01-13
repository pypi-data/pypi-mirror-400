import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel
from strawberry.types import Info


def get_mongo_projection(
    info: Info, model: Type[BaseModel]
) -> Optional[Dict[str, int]]:
    """
    Extract MongoDB projection from GraphQL query selection.

    Returns None if projection cannot be determined or if all fields
    should be returned.
    """
    if not hasattr(info, "selected_fields") or not info.selected_fields:
        return None

    projection = {}

    try:
        # Handle case where selected_fields might not be indexable
        if not isinstance(info.selected_fields, (list, tuple)):
            return None

        if len(info.selected_fields) == 0:
            return None

        root_field = info.selected_fields[0]
        if not hasattr(root_field, "selections"):
            return None

        for selection in root_field.selections:
            if hasattr(selection, "name") and not selection.name.startswith(
                "__"
            ):
                projection[selection.name] = 1
    except (IndexError, AttributeError, TypeError):
        return None

    if not projection:
        return None

    for name, field in model.model_fields.items():
        if field.is_required():
            key = field.alias or name
            projection[key] = 1

    return projection


def normalize_datetime_to_utc(value: Any) -> Any:
    """
    Recursively convert data to MongoDB format:
    1. Convert ISO strings to datetime objects if it matches the ISO format.
    2. Convert timezone-aware datetimes to UTC "naive".
    """

    ISO_DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    if isinstance(value, str) and ISO_DATE_REGEX.match(value):
        try:
            clean_value = value.replace("Z", "+00:00")
            value = datetime.fromisoformat(clean_value)
        except (ValueError, TypeError):
            return value

    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    if isinstance(value, list):
        return [normalize_datetime_to_utc(v) for v in value]

    if isinstance(value, dict):
        return {k: normalize_datetime_to_utc(v) for k, v in value.items()}

    return value


def convert_input_types_to_dict(value: Any) -> Any:
    """
    Convert recursively InputType objects to dictionaries.
    
    Strawberry InputType objects created with @strawberry.experimental.pydantic.input
    need to be converted to Pydantic models first, then to dictionaries.
    This function handles nested InputType objects recursively.
    
    Args:
        value: Value that may contain InputType objects
        
    Returns:
        Value with all InputType objects converted to dictionaries
    """
    # Check if this is an InputType (has to_pydantic method)
    if hasattr(value, "to_pydantic") and callable(getattr(value, "to_pydantic")):
        # Convert InputType to Pydantic model, then to dict
        pydantic_model = value.to_pydantic()
        if hasattr(pydantic_model, "model_dump"):
            return convert_input_types_to_dict(
                pydantic_model.model_dump(by_alias=True)
            )
        # If to_pydantic returns a dict directly (PatchInput case)
        if isinstance(pydantic_model, dict):
            return {k: convert_input_types_to_dict(v) for k, v in pydantic_model.items()}
        return convert_input_types_to_dict(pydantic_model)
    
    # Handle Pydantic models
    if isinstance(value, BaseModel):
        return convert_input_types_to_dict(value.model_dump(by_alias=True))
    
    # Handle lists
    if isinstance(value, list):
        return [convert_input_types_to_dict(v) for v in value]
    
    # Handle dictionaries
    if isinstance(value, dict):
        return {k: convert_input_types_to_dict(v) for k, v in value.items()}
    
    # Primitive types: return as-is
    return value
