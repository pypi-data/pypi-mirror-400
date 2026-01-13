from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from ..models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base class for data repositories."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model_class: type[ModelType] = model

    async def create(self, attributes: dict[str, str]) -> ModelType:
        """Creates the model instance.

        :param attributes: The attributes to create the model with.
        :return: The created model instance.
        """
        model = self.model_class(**attributes)

        await model.save()

        return model

    async def bulk_create(
        self,
        objects: Iterable[ModelType],
        batch_size: int | None = None,
        ignore_conflicts: bool = False,
        update_fields: Iterable[str] | None = None,
        on_conflict: Iterable[str] | None = None,
    ) -> list[ModelType] | None:
        """Bulk insert operation.

        The bulk insert operation will do the minimum to ensure that the object
        created in the DB has all the defaults and generated fields set,
        but may be incomplete reference in Python.

        e.g. ``IntField`` primary keys will not be populated.

        Example:
        -------
            User.bulk_create([
                User(name="...", email="..."),
                User(name="...", email="...")
            ])

        :param on_conflict: On conflict index name
        :param update_fields: Update fields when conflicts
        :param ignore_conflicts: Ignore conflicts when inserting
        :param objects: List of objects to bulk create
        :param batch_size: How many objects are created in a single query
        :param using_db: Specific DB connection to use instead of default bound

        """
        created_objects = await self.model_class.bulk_create(
            objects=objects,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_fields=update_fields,
            on_conflict=on_conflict,
        )

        return created_objects

    async def bulk_update(
        self,
        objects: Iterable[ModelType],
        fields: Iterable[str],
        batch_size: int | None = None,
    ) -> list[ModelType]:
        """Update the given fields in each of the given objects in the database.

        This method efficiently updates the given fields on the provided model instances,
        generally with one queryset.

        Example:
        -------
            users = [
                User.create(name="...", email="..."),
                User.create(name="...", email="...")
            ]
            users[0].name = 'name1'
            users[1].name = 'name2'

            User.bulk_update(users, fields=['name'])

        :param objects: List of objects to bulk create
        :param fields: The fields to update
        :param batch_size: How many objects are created in a single query
        :param using_db: Specific DB connection to use instead of default bound

        """
        updated_objects = await self.model_class.bulk_update(
            objects=objects,
            fields=fields,
            batch_size=batch_size,
        )

        return updated_objects  # type: ignore

    async def all(self) -> list[ModelType]:
        """Returns a list of model instances.

        :param skip: The number of records to skip.
        :param limit: The number of record to return.
        :return: A list of model instances.
        """
        queryset = await self.model_class.all()

        return queryset

    async def filter_by(self, **kwargs: Any) -> list[ModelType]:
        """Returns the model instance matching the field and value.

        :param field: The field to match.
        :param value: The value to match.
        :return: The model instance.
        """
        return await self.model_class.filter(**kwargs)

    async def delete(self, model: ModelType) -> None:
        """Deletes the model.

        :param model: The model to delete.
        :return: None
        """
        await model.delete()
        return
