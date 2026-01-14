import sys

import mongomock
from django.apps import AppConfig
from django.conf import settings
from mongoengine import connect


class DjangoMongoAdapterConfig(AppConfig):
    name = "smoothglue.django_mongo_adapter"

    def ready(self):
        if hasattr(settings, "MONGO_CLIENT_CONNECTION"):
            if "test" in sys.argv:
                connect(
                    alias=settings.MONGO_CLIENT_CONNECTION.get("alias", "default"),
                    mongo_client_class=mongomock.MongoClient,
                )
            else:
                connect(**settings.MONGO_CLIENT_CONNECTION)
