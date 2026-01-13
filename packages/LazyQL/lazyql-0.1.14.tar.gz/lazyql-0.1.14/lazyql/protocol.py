from typing import Any, Protocol, TypeVar

from pydantic import BaseModel


class HasToPydantic(Protocol):
    """Protocol for types that can convert to Pydantic models."""

    def to_pydantic(self) -> BaseModel: ...


class HasFromPydantic(Protocol):
    """
    Protocol for types that can be created from Pydantic models.

    Using Any for parameters and return type is necessary here as this protocol
    must work with dynamically generated Strawberry types whose exact structure
    cannot be known at static analysis time.
    """

    @classmethod
    def from_pydantic(cls, instance: Any) -> Any:  # noqa: ANN001, ANN401
        ...


TInput = TypeVar("TInput", bound=HasToPydantic)
TOutput = TypeVar("TOutput", bound=HasFromPydantic)
TFilter = TypeVar("TFilter")
