from typing import List, Optional, Type

import strawberry
from pydantic import BaseModel

from .output_type_builder import OutputTypeBuilder


def register_sub_model(
    model: Type[BaseModel],
    name: Optional[str] = None,
    exclude_fields: Optional[List[str]] = None,
) -> tuple:
    """
    Register a nested Pydantic model as GraphQL Output and Input types.

    Args:
        model: Pydantic model to register
        name: Optional custom name (defaults to model.__name__)
        exclude_fields: Fields to exclude from Output type

    Returns:
        Tuple of (OutputType, InputType)
    """
    model_name = name or model.__name__
    exclude = exclude_fields or []

    # Create Output type using the builder
    builder = OutputTypeBuilder()
    output_type = builder.build(model, model_name, exclude)

    # Create Input type
    @strawberry.experimental.pydantic.input(
        model=model, all_fields=True, name=f"{model_name}Input"
    )
    class InputType:
        pass

    return output_type, InputType
