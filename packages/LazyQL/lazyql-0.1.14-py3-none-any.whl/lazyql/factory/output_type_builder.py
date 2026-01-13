from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    get_args,
    get_origin,
    get_type_hints,
)

import strawberry
from pydantic import BaseModel as PydanticBase

from ..models import BaseDBModel


class OutputTypeBuilder:
    """Builds Strawberry Output types with field exclusion support."""

    def build(
        self, model: Type[PydanticBase], name: str, exclude_fields: List[str]
    ) -> Type:
        """Create Strawberry output type for GraphQL responses."""
        if not exclude_fields:
            return self._build_simple_output(model, name)

        return self._build_custom_output(model, name, exclude_fields)

    def _build_simple_output(
        self, model: Type[PydanticBase], name: str
    ) -> Type:
        """Build output type without field exclusions."""
        namespace = {}
        annotations = {}

        if self._is_db_model(model):
            # Expose _id directly in GraphQL
            annotations["_id"] = strawberry.ID
            namespace["_id"] = strawberry.field(
                name="_id", resolver=lambda self: self.id
            )

        namespace["__annotations__"] = annotations
        GeneratedOutput = type(f"{name}Output", (), namespace)

        return strawberry.experimental.pydantic.type(
            model=model, all_fields=True, name=f"{name}Output"
        )(GeneratedOutput)

    def _build_custom_output(
        self, model: Type[PydanticBase], name: str, exclude_fields: List[str]
    ) -> Type:
        """Build output type with field exclusions."""
        annotations = {}
        type_hints = get_type_hints(model)

        # 1. Parse exclusions once
        top_level, nested_exclusions = self._parse_exclusions(exclude_fields)

        # 2. Handle ID special case
        if (
            self._is_db_model(model)
            and "_id" not in top_level
            and "id" not in top_level
        ):
            annotations["_id"] = strawberry.ID

        # 3. Process fields
        for field_name, field_type in type_hints.items():
            if (
                field_name == "id"
                or field_name == "_id"
                or field_name in top_level
            ):
                continue

            if field_name in nested_exclusions:
                # Delegate complexity to helper
                annotations[field_name] = self._resolve_nested_field(
                    field_type, nested_exclusions[field_name]
                )
            else:
                annotations[field_name] = strawberry.auto

        # 4. Create class dynamically
        namespace = {"__annotations__": annotations}
        GeneratedOutput = type(f"{name}Output", (), namespace)

        return strawberry.experimental.pydantic.type(model=model)(
            GeneratedOutput
        )

    def _resolve_nested_field(
        self, field_type: Type, exclusions: List[str]
    ) -> Any:  # noqa: ANN001
        """
        Helper to handle recursion and optional wrapping for nested models.

        Returns:
            Strawberry type (generated dynamically) or strawberry.auto.
            Using Any is necessary here as the return type depends on runtime
            type inspection and cannot be statically determined.
        """
        base_type = self._extract_base_type(field_type)

        # Verify it's a Pydantic model we can recurse on
        if isinstance(base_type, type) and issubclass(base_type, PydanticBase):
            nested_output = self.build(
                base_type,
                base_type.__name__,
                exclusions,
            )

            # Re-apply Optional wrapper if necessary
            if self._is_optional(field_type):
                return Optional[nested_output]
            return nested_output

        return strawberry.auto

    def _parse_exclusions(
        self, exclude_fields: List[str]
    ) -> Tuple[Set[str], Dict[str, List[str]]]:
        """Separate top-level and nested exclusions."""
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

    @staticmethod
    def _extract_base_type(field_type: Type) -> Type:
        """Extract base type from Optional or complex types."""
        origin = get_origin(field_type)
        if origin is type(None) or (
            hasattr(field_type, "__args__")
            and type(None) in field_type.__args__
        ):
            args = get_args(field_type)
            return next(arg for arg in args if arg is not type(None))
        return field_type

    @staticmethod
    def _is_optional(field_type: Type) -> bool:
        """Check if field type is Optional."""
        origin = get_origin(field_type)
        return origin is type(None) or (
            hasattr(field_type, "__args__")
            and type(None) in field_type.__args__
        )

    @staticmethod
    def _is_db_model(model: Type) -> bool:
        """Check if model is a database model."""
        try:
            return issubclass(model, BaseDBModel)
        except TypeError:
            return False
