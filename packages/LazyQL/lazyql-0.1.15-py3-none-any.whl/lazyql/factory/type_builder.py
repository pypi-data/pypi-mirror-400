from typing import (
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import strawberry
from pydantic import BaseModel

from ..models import BaseDBModel
from .patch_input_helper import (
    create_patch_input_type as _create_patch_input_type,
)
from .patch_input_helper import (
    register_input_type,
)


class TypeBuilder:
    """Builds Strawberry Input/Output types from Pydantic models."""

    def create_output_type(
        self, model: Type[BaseModel], name: str, exclude_fields: List[str]
    ):
        """Create Strawberry output type for GraphQL responses."""
        if not exclude_fields:
            return self._create_simple_output(model, name)

        return self._create_filtered_output(model, name, exclude_fields)

    def create_input_type(self, model: Type[BaseModel], name: str):
        """Create Strawberry input type for mutations."""

        @strawberry.experimental.pydantic.input(
            model=model, all_fields=True, name=f"{name}Input"
        )
        class InputType:
            pass

        register_input_type(model, InputType)
        return InputType

    def create_patch_input_type(self, model: Type[BaseModel], name: str):
        """
        Crée un type d'entrée partiel (Patch) où tous les champs sont optionnels.
        Délègue à la fonction helper qui gère les sous-modèles.
        """
        return _create_patch_input_type(model, name)

    def _create_simple_output(self, model: Type[BaseModel], name: str):
        """Create output type with all fields."""

        @strawberry.experimental.pydantic.type(
            model=model, all_fields=True, name=f"{name}Output"
        )
        class OutputType:
            _id: strawberry.ID = strawberry.field(name="_id")

        return OutputType

    def _create_filtered_output(
        self, model: Type[BaseModel], name: str, exclude_fields: List[str]
    ):
        """Create output type with field exclusions."""
        type_hints = get_type_hints(model)
        top_level, nested = self._parse_exclusions(exclude_fields)

        annotations = {}
        namespace = {}

        # Add ID for DB models
        if (
            issubclass(model, BaseDBModel)
            and "_id" not in top_level
            and "id" not in top_level
        ):
            annotations["_id"] = strawberry.ID
            namespace["_id"] = strawberry.field(name="_id")

        # Add fields
        for field_name, field_type in type_hints.items():
            if (
                field_name in top_level
                or field_name == "id"
                or field_name == "_id"
            ):
                continue

            if field_name in nested:
                self._add_nested_field(
                    field_name,
                    field_type,
                    nested[field_name],
                    annotations,
                    namespace,
                )
            else:
                annotations[field_name] = strawberry.auto

        namespace["__annotations__"] = annotations
        cls = type(f"{name}Output", (), namespace)
        return strawberry.experimental.pydantic.type(model=model)(cls)

    def _parse_exclusions(self, exclude_fields: List[str]):
        """Parse exclusion list into top-level and nested."""
        top_level = set()
        nested: Dict[str, List[str]] = {}

        for exclusion in exclude_fields:
            if "." in exclusion:
                field_name, nested_path = exclusion.split(".", 1)
                if field_name not in nested:
                    nested[field_name] = []
                nested[field_name].append(nested_path)
            else:
                top_level.add(exclusion)

        return top_level, nested

    def _add_nested_field(
        self, field_name, field_type, exclusions, annotations, namespace
    ):
        """Add nested field with exclusions."""
        from typing import get_args

        base_type = field_type
        origin = get_origin(base_type)
        is_optional = False

        # Handle Optional
        if origin is type(None) or (
            hasattr(base_type, "__args__") and type(None) in base_type.__args__
        ):
            is_optional = True
            args = get_args(base_type)
            base_type = next(arg for arg in args if arg is not type(None))

        # Create nested output type
        if isinstance(base_type, type) and issubclass(base_type, BaseModel):
            nested_output = TypeBuilder().create_output_type(
                base_type, base_type.__name__, exclusions
            )

            annotations[field_name] = (
                nested_output | None if is_optional else nested_output
            )
            namespace[field_name] = strawberry.field()
