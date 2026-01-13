from typing import Any, Dict

import strawberry
from pydantic.alias_generators import to_camel

from ..utils import normalize_datetime_to_utc


class FilterParser:
    """
    Parses GraphQL filter inputs into MongoDB query format.

    New format: { field: { operator: value } }
    Example:
    {
        name: {
            contains: "test"
        }
    }
    ->
    {
        name: {
            $regex: "test",
            $options: "i"
        }
    }
    """

    def parse(self, filter_input: Any) -> Dict[str, Any]:
        """
        Convert GraphQL filter input to MongoDB query.

        Args:
            filter_input: Strawberry input object with filter values

        Returns:
            MongoDB query dictionary
        """
        if not filter_input:
            return {}
        return self._parse_dict(filter_input.__dict__)

    def _parse_dict(
        self, filter_dict: Dict[str, Any], prefix: str = ""
    ) -> Dict[str, Any]:
        """
        Parse filter dictionary into MongoDB query.

        Iterates through each field and converts its operators
        to MongoDB format. Supports nested filters via dot notation.

        Args:
            filter_dict: Dictionary of filter fields
            prefix: Prefix for nested fields (dot notation)
        """
        mongo_query: Dict[str, Any] = {}

        for field_name, operators_obj in filter_dict.items():
            # Skip unset or None values
            if self._should_skip(field_name, operators_obj):
                continue

            # Build field path with dot notation for nested fields
            field_path = (
                f"{prefix}.{to_camel(field_name)}"
                if prefix
                else to_camel(field_name)
            )

            # operators_obj is an object with operator fields
            if hasattr(operators_obj, "__dict__"):
                # Check if this is a nested filter (has __annotations__)
                if self._is_nested_filter(operators_obj):
                    # Recursively parse nested filter with dot notation
                    nested_query = self._parse_dict(
                        operators_obj.__dict__, prefix=field_path
                    )
                    mongo_query.update(nested_query)
                else:
                    # Regular operators object
                    field_query = self._parse_operators(operators_obj.__dict__)
                    if field_query is not None:
                        mongo_query[field_path] = field_query
        return mongo_query

    @staticmethod
    def _is_nested_filter(obj: Any) -> bool:
        """
        Check if object is a nested filter
        (has nested fields, not operators).
        """
        if not hasattr(obj, "__dict__"):
            return False

        # Check if any field looks like an operator (eq, gt, contains, etc.)
        common_operators = {
            "eq",
            "ne",
            "gt",
            "gte",
            "lt",
            "lte",
            "contains",
            "startsWith",
            "starts_with",
            "endsWith",
            "ends_with",
            "in_",
            "nin",
            "exists",
            "all_",
            "size",
        }

        obj_fields = {k for k in obj.__dict__.keys() if not k.startswith("_")}

        # If it has operator fields, it's not a nested filter
        if obj_fields & common_operators:
            return False

        # Otherwise, treat as nested filter
        return len(obj_fields) > 0

    def _parse_operators(
        self, operators: Dict[str, Any]
    ) -> Dict[str, Any] | Any:
        """
        Parse operators object for a single field.

        Handles special cases:
        - 'eq' operator returns direct value (not wrapped in dict)
        - Multiple operators are merged into single query object
        - Regex operators are converted to $regex format
        """
        mongo_ops = {}
        direct_value = None

        for op_name, value in operators.items():
            if self._should_skip(op_name, value):
                continue

            value = self._normalize_value(value)

            # Handle equality as direct value (MongoDB optimization)
            if op_name == "eq":
                direct_value = value
                continue

            # Handle regex operators
            if self._handle_regex_operator(op_name, value, mongo_ops):
                continue

            # Map standard operators to MongoDB equivalents
            mongo_op = self._map_operator(op_name)
            if mongo_op:
                mongo_ops[mongo_op] = value

        # Optimize: if only eq was specified, return direct value
        if direct_value is not None and not mongo_ops:
            return direct_value

        # Otherwise return the operator dict
        return mongo_ops if mongo_ops else None

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """
        Normalize value by converting datetime objects to UTC.

        Uses the shared utility function to ensure consistency with mutations.
        """
        return normalize_datetime_to_utc(value)

    def _handle_regex_operator(
        self, op_name: str, value: Any, mongo_ops: Dict[str, Any]
    ) -> bool:
        """
        Handle regex operators (contains, startsWith, endsWith).

        Returns True if the operator was handled, False otherwise.
        """
        regex_pattern = self._get_regex_pattern(op_name, value)
        if regex_pattern is None:
            return False

        mongo_ops["$regex"] = regex_pattern
        mongo_ops["$options"] = "i"  # Case-insensitive
        return True

    @staticmethod
    def _get_regex_pattern(op_name: str, value: Any) -> str | None:
        """
        Get MongoDB regex pattern for the given operator.

        Returns None if the operator is not a regex operator.
        """
        if op_name == "contains":
            return value
        if op_name in ["startsWith", "starts_with"]:
            return f"^{value}"
        if op_name in ["endsWith", "ends_with"]:
            return f"{value}$"
        return None

    def _map_operator(self, op_name: str) -> str | None:
        """
        Map GraphQL operator name to MongoDB operator.

        Handles field name mangling for reserved keywords
        """
        mapping = {
            "ne": "$ne",
            "gt": "$gt",
            "gte": "$gte",
            "lt": "$lt",
            "lte": "$lte",
            "in_": "$in",  # 'in' is reserved in Python
            "nin": "$nin",
            "exists": "$exists",
            "all_": "$all",  # 'all' is a Python builtin
            "size": "$size",
        }
        return mapping.get(op_name)

    def _should_skip(self, key: str, value: Any) -> bool:
        """
        Check if a filter field should be skipped.

        Skips:
        - None values
        - UNSET values (Strawberry's way of indicating omitted fields)
        - Private fields (starting with '_')
        """
        return (
            value is None or value is strawberry.UNSET or key.startswith("_")
        )
