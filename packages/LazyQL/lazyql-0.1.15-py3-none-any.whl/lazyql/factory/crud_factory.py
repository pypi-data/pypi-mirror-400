from typing import Dict, List, Optional, Type

from pydantic import BaseModel

from ..filters import FilterBuilder, FilterParser
from ..permissions import PermissionChecker, PermissionManager
from .mutation_builder import MutationBuilder
from .query_builder import QueryBuilder
from .type_builder import TypeBuilder


class CRUDFactoryAPI:
    """
    Factory for creating CRUD GraphQL APIs from Pydantic models.

    Orchestrates type generation, query building, and mutation building.
    """

    def __init__(self):
        self._type_builder = TypeBuilder()
        self._filter_builder = FilterBuilder()
        self._filter_parser = FilterParser()
        self._query_builder = QueryBuilder(self._filter_parser)
        self._mutation_builder = MutationBuilder()

    def create(
        self,
        model: Type[BaseModel],
        collection_name: Optional[str] = None,
        permissions: Optional[Dict[str, PermissionChecker]] = None,
        exclude_fields: Optional[List[str]] = None,
    ) -> tuple:
        """
        Create complete GraphQL Query and Mutation types for a model.

        Args:
            model: Pydantic model class defining the data structure
            collection_name: MongoDB collection name for persistence
            permissions: Dict mapping operations to permission checker
            functions
            exclude_fields: List of fields to hide from Output and filters

        Returns:
            Tuple of (Query, Mutation) Strawberry types ready for schema
        """
        name = model.__name__
        permission_manager = PermissionManager(permissions or {})
        exclude = exclude_fields or []

        # Generate GraphQL types
        output_type = self._type_builder.create_output_type(
            model, name, exclude
        )
        input_type = self._type_builder.create_input_type(model, name)
        patch_input_type = self._type_builder.create_patch_input_type(
            model, name
        )
        filter_type = self._filter_builder.build(model, name, exclude)

        # Build Query and Mutation
        query = self._query_builder.build(
            name,
            collection_name,
            model,
            output_type,
            filter_type,
            permission_manager,
        )
        mutation = self._mutation_builder.build(
            name,
            collection_name,
            model,
            input_type,
            output_type,
            permission_manager,
            patch_input_type,
        )

        return query, mutation


# Convenience function
_factory = CRUDFactoryAPI()


def create_crud_api(
    model: Type[BaseModel],
    collection_name: Optional[str] = None,
    permissions: Optional[Dict[str, PermissionChecker]] = None,
    exclude_fields: Optional[List[str]] = None,
) -> tuple:
    """
    Create CRUD API with custom permissions.

    Convenience function using the factory internally.
    """
    return _factory.create(model, collection_name, permissions, exclude_fields)
