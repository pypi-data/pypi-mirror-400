from typing import Type

import strawberry
from pydantic import BaseModel


class InputTypeBuilder:
    """Builds Strawberry Input types for mutations."""

    def build(self, model: Type[BaseModel], name: str) -> Type:
        """Create Strawberry input type for mutations (Create)."""

        @strawberry.experimental.pydantic.input(
            model=model, all_fields=True, name=f"{name}Input"
        )
        class InputType:
            pass

        return InputType

    def build_patch(self, model: Type[BaseModel], name: str) -> Type:
        """Create Strawberry input type for partial updates (Patch)."""

        @strawberry.experimental.pydantic.input(
            model=model, name=f"{name}PatchInput"
        )
        class PatchInputType:
            pass

        return PatchInputType
