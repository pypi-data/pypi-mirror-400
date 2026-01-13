import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Type

import strawberry
from pydantic import BaseModel
from pydantic.alias_generators import to_pascal
from strawberry.exceptions import GraphQLError
from strawberry.types import Info

from lazyql.utils import get_mongo_projection

from ..exceptions import InvalidDocumentIdException
from ..filters import FilterParser
from ..permissions import PermissionDenied, PermissionManager
from ..protocol import TFilter, TOutput
from ..service import LazyQL

logger = logging.getLogger(__name__)

# Constants for error messages
DB_CONNECTION_NOT_AVAILABLE = "Database connection not available"
DOCUMENT_ID_REQUIRED = "Document ID is required"


class QueryBuilder:
    """Builds GraphQL Query types with list and get_one resolvers."""

    def __init__(self, filter_parser: FilterParser):
        self._filter_parser = filter_parser

    def build(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        output_type: Type[TOutput],
        filter_type: Type[TFilter],
        permission_manager: PermissionManager,
    ):
        """
        Create Query type with list and get_one resolvers.

        Generated resolvers:
        - list: Get multiple items with filtering, pagination, and sorting
        - get_one: Get single item by ID
        """
        pascal_name = to_pascal(name)
        if collection_name is None:
            collection_name = model.__name__.lower() + "s"

        fields = {}
        fields.update(
            self._create_get_all_resolver(
                name,
                collection_name,
                model,
                output_type,
                filter_type,
                permission_manager,
            )
        )
        fields.update(
            self._create_get_one_resolver(
                name,
                collection_name,
                model,
                output_type,
                permission_manager,
            )
        )

        _Query = type(f"{pascal_name}Query", (), fields)
        return strawberry.type(_Query)

    def _get_db(self, info: Info):
        """Extract database from GraphQL info context."""
        db = info.context.get("db")
        if db is None:
            raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)
        return db

    def _parse_filters(self, filter: Optional[TFilter]) -> Optional[Dict]:
        """Parse filters with error handling."""
        try:
            return self._filter_parser.parse(filter)
        except Exception as e:
            logger.error(f"Error parsing filters: {e}")
            raise GraphQLError(f"Invalid filter format: {e}") from e

    def _create_get_all_resolver(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        output_type: Type[TOutput],
        filter_type: Type[TFilter],
        permission_manager: PermissionManager,
    ) -> dict:
        """Create get_all resolver."""
        pascal_name = to_pascal(name)

        async def resolve_get_all(
            info: Info,
            limit: Optional[int] = 100,
            skip: Optional[int] = 0,
            filter: Optional[TFilter] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[int] = 1,
        ) -> List[TOutput]:
            """Get all documents with optional filtering and pagination."""
            try:
                permission_manager.ensure_permission("list", info)
                db = self._get_db(info)
                service = LazyQL(db, collection_name, model)
                filters = self._parse_filters(filter)
                projection = get_mongo_projection(info, model)

                try:
                    results = await service.get_all(
                        limit=limit,
                        skip=skip,
                        filters=filters if filters else None,
                        sort_by=sort_by,
                        sort_order=sort_order or 1,
                        projection=projection,
                    )
                except ValueError as e:
                    raise GraphQLError(str(e)) from e

                return [output_type.from_pydantic(r) for r in results]
            except PermissionDenied as e:
                logger.warning(f"Permission denied for list: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(f"Error listing documents: {e}", exc_info=True)
                raise GraphQLError(f"Error listing documents: {e}") from e

        resolve_get_all.__annotations__["filter"] = Optional[filter_type]
        if not TYPE_CHECKING:
            resolve_get_all.__annotations__["return"] = List[output_type]

        return {f"{pascal_name}s": strawberry.field(resolver=resolve_get_all)}

    def _create_get_one_resolver(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        output_type: Type[TOutput],
        permission_manager: PermissionManager,
    ) -> dict:
        """Create get_one resolver."""
        pascal_name = to_pascal(name)

        async def resolve_get_one(info: Info, _id: str) -> Optional[TOutput]:
            """Get a single document by ID."""
            try:
                permission_manager.ensure_permission("list", info)

                if not _id:
                    raise GraphQLError(DOCUMENT_ID_REQUIRED)

                db = self._get_db(info)
                service = LazyQL(db, collection_name, model)

                try:
                    result = await service.get_one(_id)
                except InvalidDocumentIdException as e:
                    raise GraphQLError(str(e)) from e

                if result:
                    return output_type.from_pydantic(result)
                return None
            except PermissionDenied as e:
                logger.warning(f"Permission denied for get_one: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(
                    f"Error retrieving document {_id}: {e}", exc_info=True
                )
                raise GraphQLError(f"Error retrieving document: {e}") from e

        resolve_get_one.__annotations__["return"] = Optional[output_type]

        return {pascal_name: strawberry.field(resolver=resolve_get_one)}
