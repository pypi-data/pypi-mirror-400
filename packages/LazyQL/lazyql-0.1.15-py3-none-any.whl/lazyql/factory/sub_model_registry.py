from typing import List, Optional, Type

import strawberry
from pydantic import BaseModel

from .output_type_builder import OutputTypeBuilder
from .type_builder import register_input_type


def register_sub_model(
    model: Type[BaseModel],
    name: Optional[str] = None,
    exclude_fields: Optional[List[str]] = None,
) -> tuple:
    """
    Register nested Pydantic model for GraphQL schema.

    Args:
        model: Pydantic model to register
        name: Optional custom name (defaults to model.__name__)
        exclude_fields: Fields to exclude from Output type

    Returns:
        Tuple of (OutputType, InputType)
    """
    model_name = name or model.__name__
    exclude = exclude_fields or []

    # Create Output type using the builder to support field exclusions
    builder = OutputTypeBuilder()
    output_type = builder.build(model, model_name, exclude)

    # InputType doesn't support exclusions
    @strawberry.experimental.pydantic.input(
        model=model, all_fields=True, name=f"{model_name}Input"
    )
    class InputType:
        pass

    # NOUVEAU : Enregistrer le type Input dans le cache global
    register_input_type(model, InputType)

    return output_type, InputType
