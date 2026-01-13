from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class OperatorConfig:
    """Configuration for a MongoDB operator."""

    suffix: str
    mongo_operator: str
    description: str


class OperatorHandler(ABC):
    """Abstract base for operator handlers - Strategy Pattern."""

    @abstractmethod
    def can_handle(self, key: str) -> bool:
        """Check if this handler can process the given key."""
        pass

    @abstractmethod
    def parse(self, key: str, value: Any) -> tuple[str, Dict[str, Any]]:
        """Parse the filter key and value into MongoDB query."""
        pass


class ComparisonOperator(OperatorHandler):
    """Handler for comparison operators (gt, gte, lt, lte, ne)."""

    OPERATORS = {
        "_gte": "$gte",
        "_gt": "$gt",
        "_lte": "$lte",
        "_lt": "$lt",
        "_ne": "$ne",
    }

    def can_handle(self, key: str) -> bool:
        return any(key.endswith(op) for op in self.OPERATORS)

    def parse(self, key: str, value: Any) -> tuple[str, Dict[str, Any]]:
        for suffix, mongo_op in self.OPERATORS.items():
            if key.endswith(suffix):
                field = key.replace(suffix, "")
                return field, {mongo_op: value}
        raise ValueError(f"Cannot parse comparison operator from key: {key}")


class RegexOperator(OperatorHandler):
    """Handler for regex-based string operators."""

    PATTERNS = {
        "_startsWith": "^{value}",
        "_endsWith": "{value}$",
        "_contains": "{value}",
    }

    def can_handle(self, key: str) -> bool:
        return any(key.endswith(pattern) for pattern in self.PATTERNS)

    def parse(self, key: str, value: Any) -> tuple[str, Dict[str, Any]]:
        for suffix, pattern in self.PATTERNS.items():
            if key.endswith(suffix):
                field = key.replace(suffix, "")
                regex_value = pattern.format(value=value)
                return field, {"$regex": regex_value, "$options": "i"}
        raise ValueError(f"Cannot parse regex operator from key: {key}")


class ArrayOperator(OperatorHandler):
    """Handler for array operators."""

    OPERATORS = {
        "_all": "$all",
        "_nin": "$nin",
        "_in": "$in",
        "_size": "$size",
    }

    def can_handle(self, key: str) -> bool:
        return any(key.endswith(op) for op in self.OPERATORS)

    def parse(self, key: str, value: Any) -> tuple[str, Dict[str, Any]]:
        for suffix, mongo_op in self.OPERATORS.items():
            if key.endswith(suffix):
                field = key.replace(suffix, "")
                return field, {mongo_op: value}
        raise ValueError(f"Cannot parse array operator from key: {key}")


class ExistsOperator(OperatorHandler):
    """Handler for exists operator."""

    def can_handle(self, key: str) -> bool:
        return key.endswith("_exists")

    def parse(self, key: str, value: Any) -> tuple[str, Dict[str, Any]]:
        field = key.replace("_exists", "")
        return field, {"$exists": value}


class EqualityOperator(OperatorHandler):
    """Handler for direct equality (fallback)."""

    def can_handle(self, key: str) -> bool:
        return True  # Always can handle (fallback)

    def parse(self, key: str, value: Any) -> tuple[str, Dict[str, Any]]:
        return key, value  # Direct equality, no operator dict needed
