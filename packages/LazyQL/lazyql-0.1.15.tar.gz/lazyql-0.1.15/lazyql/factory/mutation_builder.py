import logging
from typing import Optional, Type

import strawberry
from pydantic import BaseModel, ValidationError
from pydantic.alias_generators import to_pascal, to_snake
from strawberry.exceptions import GraphQLError
from strawberry.types import Info

from ..exceptions import (
    DocumentNotFoundException,
    InvalidDocumentIdException,
)
from ..permissions import PermissionDenied, PermissionManager
from ..protocol import TInput, TOutput
from ..service import LazyQL
from ..utils import convert_input_types_to_dict

logger = logging.getLogger(__name__)

# Constants for error messages
DB_CONNECTION_NOT_AVAILABLE = "Database connection not available"
DOCUMENT_ID_REQUIRED = "Document ID is required"


class MutationBuilder:
    """Builds GraphQL Mutation types with CRUD resolvers."""

    def build(
        self,
        name: str,
        collection_name: Optional[str],
        model: Type[BaseModel],
        input_type: Type[TInput],
        output_type: Type[TOutput],
        permission_manager: PermissionManager,
        patch_input_type=None,
    ):
        """
        Create Mutation type with CRUD operations and permission checks.

        Generated mutations:
        - create: Insert new document with audit logging
        - update: Modify existing document with change tracking
        - delete: Remove document with audit trail
        """
        if collection_name is None:
            collection_name = model.__name__.lower() + "s"

        fields = {}
        fields.update(
            self._create_mutation(
                name,
                collection_name,
                model,
                input_type,
                output_type,
                permission_manager,
            )
        )
        fields.update(
            self._update_mutation(
                name,
                collection_name,
                model,
                patch_input_type or input_type,
                output_type,
                permission_manager,
            )
        )
        fields.update(
            self._delete_mutation(
                name, collection_name, model, permission_manager
            )
        )
        fields.update(
            self._hard_delete_mutation(
                name, collection_name, model, permission_manager
            )
        )
        fields.update(
            self._restore_mutation(
                name, collection_name, model, output_type, permission_manager
            )
        )

        _Mutation = type(f"{to_pascal(name)}Mutation", (), fields)
        return strawberry.type(_Mutation)

    def _get_db_and_user(self, info: Info) -> tuple:
        """Extract database and user from GraphQL info context."""
        db = info.context.get("db")
        user = info.context.get("user", "system")
        if db is None:
            raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)
        return db, user

    def _validate_id(self, _id: str) -> None:
        """Validate document ID is provided."""
        if not _id:
            raise GraphQLError(DOCUMENT_ID_REQUIRED)

    def _parse_input(self, input: TInput, operation: str) -> BaseModel:
        """Parse and validate input data."""
        try:
            return input.to_pydantic()
        except (AttributeError, ValidationError) as e:
            logger.error(f"Invalid input data for {operation}: {e}")
            raise GraphQLError(f"Invalid input data: {e}") from e

    def _handle_service_exceptions(
        self, _id: str, operation: str, e: Exception
    ) -> None:
        """Handle service layer exceptions."""
        if isinstance(
            e, (InvalidDocumentIdException, DocumentNotFoundException)
        ):
            raise GraphQLError(str(e)) from e
        logger.error(f"Error {operation} document {_id}: {e}", exc_info=True)
        raise GraphQLError(f"Error {operation} document: {e}") from e

    def _create_mutation(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        input_type: Type[TInput],
        output_type: Type[TOutput],
        permission_manager: PermissionManager,
    ) -> dict:
        """Create mutation resolver."""

        async def resolve_create(info: Info, input: TInput) -> TOutput:
            try:
                permission_manager.ensure_permission("create", info)
                db, user = self._get_db_and_user(info)
                service = LazyQL(db, collection_name, model)
                data = self._parse_input(input, "create")
                res = await service.create(data, user)
                return output_type.from_pydantic(res)
            except PermissionDenied as e:
                logger.warning(f"Permission denied for create: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(f"Error creating document: {e}", exc_info=True)
                raise GraphQLError(f"Error creating document: {e}") from e

        resolve_create.__annotations__["input"] = input_type
        resolve_create.__annotations__["return"] = output_type

        return {
            f"create_{to_snake(name)}": strawberry.mutation(
                resolver=resolve_create, name=f"create{to_pascal(name)}"
            )
        }

    def _update_mutation(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        input_type: Type[TInput],
        output_type: Type[TOutput],
        permission_manager: PermissionManager,
    ) -> dict:
        """Update mutation resolver."""

        async def resolve_update(
            info: Info, _id: str, input: TInput
        ) -> TOutput:
            try:
                permission_manager.ensure_permission("update", info)
                db, user = self._get_db_and_user(info)
                self._validate_id(_id)
                service = LazyQL(db, collection_name, model)
                data = input.to_pydantic()

                if hasattr(data, "model_dump"):
                    data_dict = data.model_dump(
                        exclude_unset=True, exclude={"id", "_id"}
                    )
                else:
                    data_dict = data
                    data_dict.pop("id", None)
                    data_dict.pop("_id", None)

                # Convert recursively any InputType objects to dictionaries
                data_dict = convert_input_types_to_dict(data_dict)

                try:
                    res = await service.update(
                        _id,
                        data_dict,
                        user,
                    )
                except (
                    InvalidDocumentIdException,
                    DocumentNotFoundException,
                ) as e:
                    raise GraphQLError(str(e)) from e
                return output_type.from_pydantic(res)
            except PermissionDenied as e:
                logger.warning(f"Permission denied for update: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                self._handle_service_exceptions(_id, "updating", e)

        resolve_update.__annotations__["input"] = input_type
        resolve_update.__annotations__["return"] = output_type

        return {
            f"update_{to_snake(name)}": strawberry.mutation(
                resolver=resolve_update, name=f"update{to_pascal(name)}"
            )
        }

    def _delete_mutation(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        permission_manager: PermissionManager,
    ) -> dict:
        """Delete mutation resolver."""

        async def resolve_delete(info: Info, _id: str) -> bool:
            try:
                permission_manager.ensure_permission("delete", info)
                db, user = self._get_db_and_user(info)
                self._validate_id(_id)
                service = LazyQL(db, collection_name, model)
                await service.delete(_id, user)
                return True
            except PermissionDenied as e:
                logger.warning(f"Permission denied for delete: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                self._handle_service_exceptions(_id, "deleting", e)

        return {
            f"delete_{to_snake(name)}": strawberry.mutation(
                resolver=resolve_delete, name=f"delete{to_pascal(name)}"
            )
        }

    def _hard_delete_mutation(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        permission_manager: PermissionManager,
    ) -> dict:
        """Hard delete mutation resolver."""

        async def resolve_hard_delete(info: Info, _id: str) -> bool:
            try:
                permission_manager.ensure_permission("delete", info)
                db, user = self._get_db_and_user(info)
                self._validate_id(_id)
                service = LazyQL(db, collection_name, model)
                await service.hard_delete(_id, user)
                return True
            except PermissionDenied as e:
                logger.warning(f"Permission denied for hard_delete: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                self._handle_service_exceptions(_id, "hard deleting", e)

        return {
            f"hard_delete_{to_snake(name)}": strawberry.mutation(
                resolver=resolve_hard_delete,
                name=f"hardDelete{to_pascal(name)}",
            )
        }

    def _restore_mutation(
        self,
        name: str,
        collection_name: str,
        model: Type[BaseModel],
        output_type: Type[TOutput],
        permission_manager: PermissionManager,
    ) -> dict:
        """Restore mutation resolver."""

        async def resolve_restore(info: Info, _id: str) -> TOutput:
            try:
                permission_manager.ensure_permission("update", info)
                db, user = self._get_db_and_user(info)
                self._validate_id(_id)
                service = LazyQL(db, collection_name, model)
                res = await service.restore(_id, user)
                return output_type.from_pydantic(res)
            except PermissionDenied as e:
                logger.warning(f"Permission denied for restore: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                self._handle_service_exceptions(_id, "restoring", e)

        resolve_restore.__annotations__["return"] = output_type

        return {
            f"restore_{to_snake(name)}": strawberry.mutation(
                resolver=resolve_restore, name=f"restore{to_pascal(name)}"
            )
        }
