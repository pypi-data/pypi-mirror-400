from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    get_args,
    get_origin,
    get_type_hints,
)

import strawberry
from pydantic import BaseModel

from .type_generator import FilterFieldGenerator, TypeInspector


class FilterBuilder:
    """
    Builds GraphQL filter input types from Pydantic models.

    Follows Single Responsibility Principle: Only responsible for
    transforming Pydantic models into Strawberry filter types.
    """

    def __init__(self):
        self._generator = FilterFieldGenerator()
        self._inspector = TypeInspector()
        self._cache = {}

    def clear_cache(self):
        """Clear the internal cache. Useful for testing."""
        self._cache.clear()

    def build(
        self,
        model: Type[BaseModel],
        name: str,
        exclude_from_filters: Optional[List[str]] = None,
    ):
        """
        Build a Strawberry filter input type from a Pydantic model.

        New format creates nested operator objects:
        { field: { operator: value } }

        Example:
            { name: { contains: "test" }, age: { gte: 18 } }

        Args:
            model: Pydantic model to generate filters for
            name: Base name for the generated filter type
            exclude_from_filters: List of field names to exclude from filters
                                 Supports dot notation for nested fields:
                                 ["secret", "address.internal_code"]

        Returns:
            Strawberry input type with filter fields
        """
        # Create cache key that includes exclusions to avoid conflicts
        excluded = set(exclude_from_filters or [])
        cache_key = (name, tuple(sorted(excluded)))

        if cache_key in self._cache:
            return self._cache[cache_key]

        type_hints = get_type_hints(model)
        filter_fields = {}

        for field_name, field_type in type_hints.items():
            # Skip internal audit fields - they shouldn't be filterable
            if self._inspector.is_internal_field(field_name):
                continue

            # Skip secret fields - explicitly excluded from filters (top-level)
            if field_name in excluded:
                continue

            # Check for nested exclusions (e.g., "address.secret")
            nested_exclusions = self._get_nested_exclusions(
                field_name, excluded
            )

            operator_type = self._generate_field_operators(
                field_type, nested_exclusions
            )
            if operator_type:
                filter_fields[field_name] = operator_type

        input_type = self._create_strawberry_input(name, filter_fields)
        self._cache[cache_key] = input_type

        return input_type

    def _get_nested_exclusions(
        self, field_name: str, excluded: set[str]
    ) -> List[str]:
        """
        Extract nested exclusions for a given field.

        Example:
            field_name = "address"
            excluded = {"address.street", "address.city"}
            returns ["street", "city"]
        """
        prefix = f"{field_name}."
        nested = []
        for exclusion in excluded:
            if exclusion.startswith(prefix):
                # Remove the prefix to get the nested field name
                prefix_len = len(prefix)
                nested_field = exclusion[prefix_len:]
                nested.append(nested_field)
        return nested

    def _generate_field_operators(
        self,
        field_type: Type,
        nested_exclusions: Optional[List[str]] = None,
    ):
        """
        Generate appropriate operator type for a field based on its type.

        Maps Python types to their corresponding operator sets:
        - str -> StringOperators (contains, startsWith, etc.)
        - int/float -> NumericOperators (gt, gte, lt, lte, etc.)
        - bool -> BooleanOperators (eq, exists)
        - list -> ListOperators (in, all, size, etc.)
        - Pydantic models -> Nested filters (recursive)
        """
        base_type = self._extract_base_type(field_type)
        origin = get_origin(base_type)
        args = get_args(base_type)

        # Handle list types - generate list-specific operators
        if origin is list and args:
            elem_type = args[0]
            # Only support lists of primitive types for filtering
            if elem_type in [str, int, float, datetime]:
                return self._generator.generate_list_operators(elem_type)
            if self._is_pydantic_model(elem_type):
                return self._generate_field_operators(
                    elem_type, nested_exclusions
                )
            return None

        # Handle nested Pydantic models
        if self._is_pydantic_model(base_type):
            return self._generate_nested_filter(base_type, nested_exclusions)

        # Handle scalar types with appropriate operator sets
        if self._inspector.is_string(base_type):
            return self._generator.generate_string_operators()

        if self._inspector.is_numeric(base_type):
            return self._generator.generate_numeric_operators(base_type)

        if self._inspector.is_datetime(base_type):
            return self._generator.generate_datetime_operators()

        if self._inspector.is_boolean(base_type):
            return self._generator.generate_boolean_operators()

        if self._inspector.is_enum(base_type):
            # Enums are treated as strings in filters
            return self._generator.generate_enum_operators()

        return None

    @staticmethod
    def _extract_base_type(field_type: Type) -> Type:
        """
        Extract base type from Optional/Union wrapper.

        Example: Optional[str] -> str
        """
        origin = get_origin(field_type)
        args = get_args(field_type)

        # Check if this is an Optional (Union with None)
        if origin is type(None) or (args and type(None) in args) and args:
            return next(
                (arg for arg in args if arg is not type(None)), field_type
            )

        return field_type

    @staticmethod
    def _create_strawberry_input(name: str, filter_fields: Dict[str, Type]):
        """
        Create Strawberry input type dynamically from filter fields.

        All fields default to UNSET to support optional filtering.
        """
        class_dict: Dict[str, Any] = {"__annotations__": {}}

        for field_name, operator_type in filter_fields.items():
            # Make all filter fields optional with UNSET as default
            class_dict["__annotations__"][field_name] = operator_type | None
            class_dict[field_name] = strawberry.UNSET

        filter_class = type(f"{name}Filter", (), class_dict)
        return strawberry.input(filter_class, name=f"{name}Filter")

    @staticmethod
    def _is_pydantic_model(field_type: Type) -> bool:
        """Check if type is a Pydantic model."""
        try:
            return (
                isinstance(field_type, type)
                and issubclass(field_type, BaseModel)
                and field_type is not BaseModel
            )
        except TypeError:
            return False

    def _generate_nested_filter(
        self,
        model: Type[BaseModel],
        exclude_fields: Optional[List[str]] = None,
    ) -> Type:
        """Generate filter type for nested Pydantic model (recursive)."""
        # Build nested filter recursively with nested exclusions
        nested_filter = self.build(
            model, model.__name__, exclude_from_filters=exclude_fields or []
        )
        return nested_filter
