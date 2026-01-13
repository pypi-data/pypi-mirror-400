from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Type, Union

import strawberry


@strawberry.input
class StringOperators:
    """String field operators."""

    eq: Optional[str] = strawberry.UNSET
    ne: Optional[str] = strawberry.UNSET
    contains: Optional[str] = strawberry.UNSET
    starts_with: Optional[str] = strawberry.field(
        default=strawberry.UNSET, name="startsWith"
    )
    ends_with: Optional[str] = strawberry.field(
        default=strawberry.UNSET, name="endsWith"
    )
    in_: Optional[List[str]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[str]] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class IntOperators:
    """Integer field operators."""

    eq: Optional[int] = strawberry.UNSET
    ne: Optional[int] = strawberry.UNSET
    gt: Optional[int] = strawberry.UNSET
    gte: Optional[int] = strawberry.UNSET
    lt: Optional[int] = strawberry.UNSET
    lte: Optional[int] = strawberry.UNSET
    in_: Optional[List[int]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[int]] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class FloatOperators:
    """Float field operators."""

    eq: Optional[float] = strawberry.UNSET
    ne: Optional[float] = strawberry.UNSET
    gt: Optional[float] = strawberry.UNSET
    gte: Optional[float] = strawberry.UNSET
    lt: Optional[float] = strawberry.UNSET
    lte: Optional[float] = strawberry.UNSET
    in_: Optional[List[float]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[float]] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class DateTimeOperators:
    """DateTime field operators."""

    eq: Optional[datetime] = strawberry.UNSET
    ne: Optional[datetime] = strawberry.UNSET
    gt: Optional[datetime] = strawberry.UNSET
    gte: Optional[datetime] = strawberry.UNSET
    lt: Optional[datetime] = strawberry.UNSET
    lte: Optional[datetime] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class BooleanOperators:
    """Boolean field operators."""

    eq: Optional[bool] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class StringListOperators:
    """String list field operators."""

    in_: Optional[List[str]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[str]] = strawberry.UNSET
    all_: Optional[List[str]] = strawberry.field(
        default=strawberry.UNSET, name="all"
    )
    size: Optional[int] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class IntListOperators:
    """Integer list field operators."""

    in_: Optional[List[int]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[int]] = strawberry.UNSET
    all_: Optional[List[int]] = strawberry.field(
        default=strawberry.UNSET, name="all"
    )
    size: Optional[int] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class FloatListOperators:
    """Float list field operators."""

    in_: Optional[List[float]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[float]] = strawberry.UNSET
    all_: Optional[List[float]] = strawberry.field(
        default=strawberry.UNSET, name="all"
    )
    size: Optional[int] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


@strawberry.input
class DateTimeListOperators:
    """DateTime list field operators."""

    in_: Optional[List[datetime]] = strawberry.field(
        default=strawberry.UNSET, name="in"
    )
    nin: Optional[List[datetime]] = strawberry.UNSET
    all_: Optional[List[datetime]] = strawberry.field(
        default=strawberry.UNSET, name="all"
    )
    size: Optional[int] = strawberry.UNSET
    exists: Optional[bool] = strawberry.UNSET


class FilterFieldGenerator:
    """
    Generates filter fields for different Python types.

    Follows Single Responsibility Principle: Only responsible for
    determining which operator type to use for a given field type.
    """

    @staticmethod
    def generate_string_operators() -> Type:
        """Generate operators type for string fields."""
        return StringOperators

    @staticmethod
    def generate_numeric_operators(
        field_type: Union[Type[int], Type[float], Type[Decimal]],
    ) -> Type:
        """
        Generate operators type for numeric fields.

        Args:
            field_type: Numeric type (int, float, or Decimal)

        Returns:
            Appropriate operator type for the numeric field
        """
        if field_type is int:
            return IntOperators
        elif field_type is float or field_type is Decimal:
            return FloatOperators
        return IntOperators  # Fallback

    @staticmethod
    def generate_datetime_operators() -> Type:
        """Generate operators type for datetime fields."""
        return DateTimeOperators

    @staticmethod
    def generate_boolean_operators() -> Type:
        """Generate operators type for boolean fields."""
        return BooleanOperators

    @staticmethod
    def generate_list_operators(
        elem_type: Union[Type[str], Type[int], Type[float], Type[datetime]],
    ) -> Type:
        """
        Generate operators type for list fields.

        Args:
            elem_type: Type of list elements (str, int, float, or datetime)

        Returns:
            Appropriate operator type for the list field
        """
        if elem_type is str:
            return StringListOperators
        elif elem_type is int:
            return IntListOperators
        elif elem_type is float:
            return FloatListOperators
        elif elem_type is datetime:
            return DateTimeListOperators
        return StringListOperators  # Fallback

    @staticmethod
    def generate_enum_operators() -> Type:
        """Generate operators type for enum fields."""
        return StringOperators  # Enums use string operators


class TypeInspector:
    """
    Inspects Python types and categorizes them.

    Follows Single Responsibility Principle: Only responsible for
    type checking and categorization logic.
    """

    NUMERIC_TYPES = (int, float, Decimal)
    # Internal fields that shouldn't appear in user-facing filters
    INTERNAL_FIELDS = {
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }

    @classmethod
    def is_internal_field(cls, field_name: str) -> bool:
        """Check if field is an internal audit field that should be hidden."""
        return field_name in cls.INTERNAL_FIELDS

    @staticmethod
    def is_string(field_type: Type) -> bool:
        """Check if type is string."""
        return field_type is str

    @classmethod
    def is_numeric(cls, field_type: Type) -> bool:
        """Check if type is numeric."""
        return field_type in cls.NUMERIC_TYPES

    @staticmethod
    def is_datetime(field_type: Type) -> bool:
        """Check if type is datetime."""
        return field_type is datetime

    @staticmethod
    def is_boolean(field_type: Type) -> bool:
        """Check if type is boolean."""
        return field_type is bool

    @staticmethod
    def is_enum(field_type: Type) -> bool:
        """Check if type is enum."""
        return isinstance(field_type, type) and issubclass(field_type, Enum)
