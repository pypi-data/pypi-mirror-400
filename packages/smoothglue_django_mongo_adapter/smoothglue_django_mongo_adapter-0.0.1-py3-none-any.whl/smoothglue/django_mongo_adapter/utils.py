from functools import reduce
from unittest import mock

import mongomock
from django.contrib import admin
from mongoengine.errors import DoesNotExist


def mock_mongo_connection():
    return mock.patch("mongoengine.connect", new=mongomock.MongoClient)


# pylint: disable=too-few-public-methods
class MockQuery:
    """
    A mock query object to satisfy the Django admin's expectations.
    """

    def __init__(self):
        self.order_by = []

    def select_related(self, *_fields):  # pylint: disable=unused-argument
        return None


class BaseMongoQuerySetWrapper:
    """
    A base wrapper for a MongoEngine QuerySet to make it compatible with the Django admin.
    Subclasses must implement the `to_django_instance` method.
    """

    def __init__(self, queryset, model):
        self.queryset = queryset
        self.query = MockQuery()
        self.model = model

    def to_django_instance(self, mongo_obj):
        """
        Convert a MongoEngine document instance to a Django model instance.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement to_django_instance")

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self.queryset[item], self.model)

        mongo_obj = self.queryset[item]
        return self.to_django_instance(mongo_obj)

    def get(self, *args, **kwargs):
        try:
            mongo_obj = self.queryset.get(*args, **kwargs)
            return self.to_django_instance(mongo_obj)
        except DoesNotExist as e:
            raise self.model.DoesNotExist from e

    def __len__(self):
        return self.queryset.count()

    def count(self):
        return self.queryset.count()

    def _clone(self):
        return self.__class__(self.queryset, self.model)

    def filter(self, *args, **kwargs):
        # Pass filtering through to the MongoEngine QuerySet.
        return self.__class__(self.queryset.filter(*args, **kwargs), self.model)

    def order_by(self, *field_names):
        # Pass ordering through to the MongoEngine QuerySet.
        return self.__class__(self.queryset.order_by(*field_names), self.model)

    def all(self):
        return self


class AutoMongoQuerySetWrapper(BaseMongoQuerySetWrapper):
    """
    A generic wrapper that automatically maps MongoEngine document fields
    to Django model fields by name.
    """

    def __init__(self, queryset, model, mapper=None):
        super().__init__(queryset, model)
        self.mapper = mapper or {}

    def _clone(self):
        # Ensure cloning preserves the mapper
        return self.__class__(self.queryset, self.model, self.mapper)

    def to_django_instance(self, mongo_obj):
        # Create a new instance of the Django model
        django_obj = self.model()

        # Automatically map fields that exist in both the mongo doc and django model
        # We use the django model's fields as the source of truth for what to populate
        for field in self.model._meta.get_fields():
            # 1. Check if there is an explicit mapping for this field
            if field.name in self.mapper:
                source_path = self.mapper[field.name]
                try:
                    # Support dotted paths like "site.name"
                    val = reduce(getattr, source_path.split("."), mongo_obj)
                    setattr(django_obj, field.name, val)
                except AttributeError:
                    # If traversal fails, leave as default/None
                    pass

            # 2. Otherwise, check for direct name match
            elif hasattr(mongo_obj, field.name):
                setattr(django_obj, field.name, getattr(mongo_obj, field.name))

        # Always attach the original document for access to extra data/methods
        django_obj.mongo_document = mongo_obj

        return django_obj


class MongoModelAdmin(admin.ModelAdmin):
    """
    A ModelAdmin subclass that automatically wires up a MongoDB backing store.
    Set `mongo_document` to your MongoEngine Document class.
    """

    mongo_document = None
    mongo_mapper = None

    def get_queryset(self, request):
        if not self.mongo_document:
            raise ValueError(
                "MongoModelAdmin must have a 'mongo_document' attribute set."
            )
        return AutoMongoQuerySetWrapper(
            self.mongo_document.objects.all(), self.model, mapper=self.mongo_mapper
        )
