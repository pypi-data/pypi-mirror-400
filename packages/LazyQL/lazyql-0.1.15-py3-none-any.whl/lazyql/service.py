import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import (
    AsyncContextManager,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from bson import ObjectId
from bson import errors as bson_errors
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorClientSession,
    AsyncIOMotorDatabase,
)
from pydantic import BaseModel, TypeAdapter, ValidationError

from .audit import log_audit
from .exceptions import (
    DocumentNotFoundException,
    InvalidDocumentIdException,
)
from .utils import normalize_datetime_to_utc

logger = logging.getLogger(__name__)

# Constants
USER_MUST_BE_NON_EMPTY_STRING = "user must be a non-empty string"

T = TypeVar("T", bound=BaseModel)


class LazyQL(Generic[T]):
    """
    Generic CRUD service with built-in audit logging and ACID transactions.

    Provides a clean, type-safe interface for MongoDB operations with:
    - Automatic audit logging
    - Soft delete support
    - Transaction support when client is provided
    - Input validation
    - Structured error handling
    """

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        collection_name: str,
        model_cls: Type[T],
        client: Optional[AsyncIOMotorClient] = None,
    ):
        if not collection_name or not isinstance(collection_name, str):
            raise ValueError("collection_name must be a non-empty string")
        if not issubclass(model_cls, BaseModel):
            raise TypeError("model_cls must be a subclass of BaseModel")

        self.db = db
        self.collection = db[collection_name]
        self.model_cls = model_cls
        self.collection_name = collection_name
        self.client = client
        self.list_adapter = TypeAdapter(List[model_cls])

        logger.debug(
            f"Initialized LazyQL service for {model_cls.__name__} "
            f"on collection '{collection_name}'"
        )

    async def get_all(
        self,
        limit: Optional[int] = 100,
        skip: Optional[int] = 0,
        filters: Optional[Dict] = None,
        sort_by: Optional[str] = None,
        sort_order: int = 1,
        include_deleted: bool = False,
        projection: Optional[Dict] = None,
    ) -> List[T]:
        """
        Get all documents with optional filtering, pagination, sorting and
        soft-delete handling.

        Args:
            limit: Maximum number of documents to return (default: 100)
            skip: Number of documents to skip (default: 0)
            filters: MongoDB query dictionary for filtering
            sort_by: Field name to sort by
            sort_order: Sort direction (1=ascending, -1=descending)
            include_deleted: If True, include soft-deleted documents

        Returns:
            List of model instances

        Raises:
            ValidationError: If document data doesn't match model schema
        """
        # Input validation
        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative")
        if skip is not None and skip < 0:
            raise ValueError("skip must be non-negative")
        if sort_order not in (1, -1):
            raise ValueError(
                "sort_order must be 1 (ascending) or -1 (descending)"
            )

        query = filters.copy() if filters else {}

        # Soft Delete: Exclude documents with deleted_at set
        if not include_deleted:
            query["deleted_at"] = None

        try:
            cursor = self.collection.find(query, projection)

            if skip is not None:
                cursor = cursor.skip(skip)
            if limit is not None:
                cursor = cursor.limit(limit)

            if sort_by:
                cursor = cursor.sort(sort_by, sort_order)

            raw_docs = await cursor.to_list(length=limit)
            if not raw_docs:
                return []

            return self._validate_documents(raw_docs)
        except Exception as e:
            logger.error(
                f"Error retrieving documents from "
                f"'{self.collection_name}': {e}",
                exc_info=True,
            )
            raise

    def _validate_documents(self, raw_docs: List[Dict]) -> List[T]:
        """
        Validate documents with fallback to individual validation.

        Tries batch validation first for optimal performance.
        Falls back to individual validation if batch fails to continue
        processing valid documents.

        Args:
            raw_docs: List of raw MongoDB documents

        Returns:
            List of validated model instances
        """
        # Try batch validation first for optimal performance
        try:
            return self.list_adapter.validate_python(raw_docs)
        except ValidationError:
            # If batch validation fails, validate individually
            # to continue processing valid documents
            validated_docs = []
            for doc in raw_docs:
                try:
                    validated_doc = self.model_cls.model_validate(doc)
                    validated_docs.append(validated_doc)
                except ValidationError as e:
                    doc_id = doc.get("_id", "unknown")
                    logger.warning(
                        f"Validation error for document {doc_id} in "
                        f"'{self.collection_name}': {e}. "
                        f"Skipping document."
                    )
                    continue

            return validated_docs

    async def get_one(self, doc_id: str) -> Optional[T]:
        """
        Get a single document by ID.

        Args:
            doc_id: Document ID (must be a valid ObjectId string)

        Returns:
            Model instance if found, None otherwise

        Raises:
            InvalidDocumentIdException: If doc_id is not a valid ObjectId
            ValidationError: If document data doesn't match model schema
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError("doc_id must be a non-empty string")

        try:
            object_id = ObjectId(doc_id)
        except (bson_errors.InvalidId, TypeError) as e:
            raise InvalidDocumentIdException(
                f"Invalid document ID format: {doc_id}"
            ) from e

        try:
            doc = await self.collection.find_one(
                {"_id": object_id, "deleted_at": None}
            )
            if not doc:
                logger.debug(
                    f"Document {doc_id} not found in '{self.collection_name}'"
                )
                return None

            return self.model_cls(**doc)
        except ValidationError as e:
            logger.error(
                f"Validation error for document {doc_id} "
                f"in collection '{self.collection_name}': {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving document {doc_id} "
                f"from '{self.collection_name}': {e}",
                exc_info=True,
            )
            raise

    @asynccontextmanager
    async def _get_session(
        self,
    ) -> AsyncContextManager[Optional[AsyncIOMotorClientSession]]:
        """
        Context manager for database sessions with transaction support.

        Returns a session if client is available, otherwise None.
        """
        if self.client:
            async with await self.client.start_session() as session:
                async with session.start_transaction():
                    yield session
        else:
            yield None

    async def create(self, data: BaseModel, user: str = "system") -> T:
        """
        Create a new document with audit logging.

        Args:
            data: Pydantic model instance with document data
            user: User identifier for audit logging (default: "system")

        Returns:
            Created model instance with generated ID

        Raises:
            ValueError: If data is invalid
            ValidationError: If document data doesn't match model schema
        """
        if not isinstance(data, BaseModel):
            raise ValueError("data must be a BaseModel instance")
        if not user or not isinstance(user, str):
            raise ValueError(USER_MUST_BE_NON_EMPTY_STRING)

        async with self._get_session() as session:
            return await self._create_implementation(data, user, session)

    async def _create_implementation(
        self,
        data: BaseModel,
        user: str,
        session: Optional[AsyncIOMotorClientSession],
    ) -> T:
        """
        Internal implementation of document creation.

        Args:
            data: Pydantic model instance
            user: User identifier
            session: Optional database session

        Returns:
            Created model instance
        """
        try:
            doc = data.model_dump(by_alias=True, exclude={"id"})

            # Normalize all datetime values to UTC (naive) for MongoDB compatibility
            doc = normalize_datetime_to_utc(doc)

            now = datetime.now(timezone.utc)
            doc.update(
                {
                    "created_at": now,
                    "updated_at": now,
                    "created_by": user,
                    "updated_by": user,
                    "deleted_at": None,
                }
            )

            result = await self.collection.insert_one(doc, session=session)
            doc["_id"] = result.inserted_id

            logger.info(
                f"Created document {result.inserted_id} "
                f"in '{self.collection_name}' by user '{user}'"
            )

            await log_audit(
                self.db,
                self.collection_name,
                result.inserted_id,
                user,
                "CREATE",
                session=session,
            )

            return self.model_cls(**doc)
        except Exception as e:
            logger.error(
                f"Error creating document in '{self.collection_name}': {e}",
                exc_info=True,
            )
            raise

    async def update(self, id: str, data: BaseModel, user: str) -> T:
        """
        Update an existing document with audit logging.

        Args:
            id: Document ID to update
            data: Pydantic model instance with update data
            user: User identifier for audit logging

        Returns:
            Updated model instance

        Raises:
            InvalidDocumentIdException: If id is not a valid ObjectId
            DocumentNotFoundException: If document doesn't exist
            ValueError: If data or user is invalid
        """
        if not isinstance(data, (BaseModel, dict)):
            raise ValueError("data must be a BaseModel instance or a dictionary")

        if not user or not isinstance(user, str):
            raise ValueError(USER_MUST_BE_NON_EMPTY_STRING)

        async with self._get_session() as session:
            return await self._update_implementation(id, data, user, session)

    async def _update_implementation(
        self,
        id: str,
        data: Union[BaseModel, Dict],
        user: str,
        session: Optional[AsyncIOMotorClientSession],
    ) -> T:
        """
        Implémentation interne de la mise à jour de document.
        Supporte les instances BaseModel et les dictionnaires bruts (Partial Updates).
        """
        try:
            try:
                object_id = ObjectId(id)
            except (bson_errors.InvalidId, TypeError) as e:
                raise InvalidDocumentIdException(
                    f"Invalid document ID format: {id}"
                ) from e

            # 1. Récupération de l'ancien document pour l'audit
            old_doc = await self.collection.find_one(
                {"_id": object_id, "deleted_at": None}, session=session
            )
            if not old_doc:
                raise DocumentNotFoundException(
                    f"Document with id {id} not found or is deleted"
                )

            # 2. Extraction intelligente des données
            if isinstance(data, BaseModel):
                # Si c'est un modèle Pydantic, on utilise model_dump avec exclude_unset
                update_data = data.model_dump(exclude_unset=True, exclude={"id", "_id"}, by_alias=True)
            else:
                # Si c'est un dictionnaire (cas du PatchInput), on copie et nettoie les IDs
                update_data = data.copy()
                update_data.pop("id", None)
                update_data.pop("_id", None)

            # 3. Vérification s'il y a des modifications à effectuer
            if not update_data:
                logger.warning(f"No fields to update for document {id} in '{self.collection_name}'")
                return self.model_cls(**old_doc)

            # 4. Normalisation et métadonnées système
            update_data = normalize_datetime_to_utc(update_data)
            update_data.update({
                "updated_at": datetime.now(timezone.utc),
                "updated_by": user
            })

            # 5. Exécution de la mise à jour partielle via $set
            new_doc = await self.collection.find_one_and_update(
                {"_id": object_id},
                {"$set": update_data},
                return_document=True,
                session=session,
            )

            if not new_doc:
                raise DocumentNotFoundException(
                    f"Document with id {id} not found after update"
                )

            # 6. Logging et Audit
            logger.info(f"Updated document {id} in '{self.collection_name}' by user '{user}'")

            await log_audit(
                self.db,
                self.collection_name,
                id,
                user,
                "UPDATE",
                old_doc,
                new_doc,
                session=session,
            )

            return self.model_cls(**new_doc)

        except (DocumentNotFoundException, InvalidDocumentIdException):
            raise
        except Exception as e:
            logger.error(
                f"Error updating document {id} in '{self.collection_name}': {e}",
                exc_info=True,
            )
            raise

    async def delete(self, id: str, user: str) -> None:
        """
        Soft delete a document (sets deleted_at timestamp).

        Args:
            id: Document ID to delete
            user: User identifier for audit logging

        Raises:
            InvalidDocumentIdException: If id is not a valid ObjectId
            DocumentNotFoundException: If document doesn't exist
            ValueError: If user is invalid
        """
        if not user or not isinstance(user, str):
            raise ValueError(USER_MUST_BE_NON_EMPTY_STRING)

        async with self._get_session() as session:
            await self._delete_implementation(id, user, session)

    async def _delete_implementation(
        self, id: str, user: str, session: Optional[AsyncIOMotorClientSession]
    ) -> None:
        """
        Internal implementation of soft delete.

        Args:
            id: Document ID
            user: User identifier
            session: Optional database session
        """
        try:
            try:
                object_id = ObjectId(id)
            except (bson_errors.InvalidId, TypeError) as e:
                raise InvalidDocumentIdException(
                    f"Invalid document ID format: {id}"
                ) from e

            old_doc = await self.collection.find_one(
                {"_id": object_id, "deleted_at": None}, session=session
            )
            if not old_doc:
                raise DocumentNotFoundException(
                    f"Document with id {id} not found or already deleted"
                )

            await self.collection.update_one(
                {"_id": object_id},
                {
                    "$set": {
                        "deleted_at": datetime.now(timezone.utc),
                        "updated_by": user,
                    }
                },
                session=session,
            )

            logger.info(
                f"Soft deleted document {id} "
                f"in '{self.collection_name}' by user '{user}'"
            )

            await log_audit(
                self.db,
                self.collection_name,
                id,
                user,
                "DELETE",
                old_doc,
                None,
                session=session,
            )
        except (DocumentNotFoundException, InvalidDocumentIdException):
            raise
        except Exception as e:
            logger.error(
                f"Error deleting document {id} in "
                f"'{self.collection_name}': {e}",
                exc_info=True,
            )
            raise

    async def hard_delete(self, id: str, user: str) -> None:
        """
        Permanently delete a document from the collection.

        WARNING: This operation cannot be undone. Use with caution.

        Args:
            id: Document ID to permanently delete
            user: User identifier for audit logging

        Raises:
            InvalidDocumentIdException: If id is not a valid ObjectId
            ValueError: If user is invalid
        """
        if not user or not isinstance(user, str):
            raise ValueError(USER_MUST_BE_NON_EMPTY_STRING)

        async with self._get_session() as session:
            await self._hard_delete_implementation(id, user, session)

    async def _hard_delete_implementation(
        self, id: str, user: str, session: Optional[AsyncIOMotorClientSession]
    ) -> None:
        """
        Internal implementation of hard delete.

        Args:
            id: Document ID
            user: User identifier
            session: Optional database session
        """
        try:
            try:
                object_id = ObjectId(id)
            except (bson_errors.InvalidId, TypeError) as e:
                raise InvalidDocumentIdException(
                    f"Invalid document ID format: {id}"
                ) from e

            result = await self.collection.delete_one(
                {"_id": object_id}, session=session
            )

            if result.deleted_count == 0:
                logger.warning(
                    f"Hard delete attempted on non-existent document {id} "
                    f"in '{self.collection_name}'"
                )
            else:
                logger.warning(
                    f"Hard deleted document {id} "
                    f"in '{self.collection_name}' by user '{user}'"
                )

            await log_audit(
                self.db,
                self.collection_name,
                id,
                user,
                "HARD_DELETE",
                session=session,
            )
        except InvalidDocumentIdException:
            raise
        except Exception as e:
            logger.error(
                f"Error hard deleting document {id} in "
                f"'{self.collection_name}': {e}",
                exc_info=True,
            )
            raise

    async def restore(self, id: str, user: str) -> T:
        """
        Restore a soft-deleted document (sets deleted_at to None).

        Args:
            id: Document ID to restore
            user: User identifier for audit logging

        Returns:
            Restored model instance

        Raises:
            InvalidDocumentIdException: If id is not a valid ObjectId
            DocumentNotFoundException: If document doesn't exist "
                "or isn't deleted
            ValueError: If user is invalid
        """
        if not user or not isinstance(user, str):
            raise ValueError(USER_MUST_BE_NON_EMPTY_STRING)

        async with self._get_session() as session:
            return await self._restore_implementation(id, user, session)

    async def _restore_implementation(
        self, id: str, user: str, session: Optional[AsyncIOMotorClientSession]
    ) -> T:
        """
        Internal implementation of document restore.

        Args:
            id: Document ID
            user: User identifier
            session: Optional database session

        Returns:
            Restored model instance
        """
        try:
            try:
                object_id = ObjectId(id)
            except (bson_errors.InvalidId, TypeError) as e:
                raise InvalidDocumentIdException(
                    f"Invalid document ID format: {id}"
                ) from e

            old_doc = await self.collection.find_one(
                {"_id": object_id, "deleted_at": {"$ne": None}},
                session=session,
            )
            if not old_doc:
                raise DocumentNotFoundException(
                    f"Document with id {id} not found or not deleted"
                )

            new_doc = await self.collection.find_one_and_update(
                {"_id": object_id},
                {"$set": {"deleted_at": None, "updated_by": user}},
                return_document=True,
                session=session,
            )

            if not new_doc:
                raise DocumentNotFoundException(
                    f"Document with id {id} not found after restore"
                )

            logger.info(
                f"Restored document {id} in "
                f"'{self.collection_name}' by user '{user}'"
            )

            await log_audit(
                self.db,
                self.collection_name,
                id,
                user,
                "RESTORE",
                old_doc,
                new_doc,
                session=session,
            )
            return self.model_cls(**new_doc)
        except (DocumentNotFoundException, InvalidDocumentIdException):
            raise
        except Exception as e:
            logger.error(
                f"Error restoring document {id} in "
                f"'{self.collection_name}': {e}",
                exc_info=True,
            )
            raise
