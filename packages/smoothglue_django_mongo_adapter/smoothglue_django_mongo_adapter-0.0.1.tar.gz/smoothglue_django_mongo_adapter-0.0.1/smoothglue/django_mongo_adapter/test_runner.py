import mongomock
from django.conf import settings
from django.test.runner import DiscoverRunner
from mongoengine import connect, disconnect_all
from mongoengine.connection import ConnectionFailure, get_connection


class MongoMockTestRunner(DiscoverRunner):
    def teardown_databases(self, old_config, **kwargs):
        try:
            connection = get_connection()
            # Assuming settings.MONGO_DATABASES["test"]["db"] exists
            connection.drop_database(settings.MONGO_DATABASES["test"]["db"])
            disconnect_all()
        except ConnectionFailure:
            pass
        return super().teardown_databases(old_config, **kwargs)

    def setup_databases(self, **kwargs):
        alias = settings.MONGO_CLIENT_CONNECTION.get("alias", "default")
        try:
            connection = get_connection(alias)
            if not isinstance(connection, mongomock.MongoClient):
                disconnect_all()
                connect(
                    alias=alias,
                    mongo_client_class=mongomock.MongoClient,
                )
        except ConnectionFailure:
            connect(
                alias=alias,
                mongo_client_class=mongomock.MongoClient,
            )
        return super().setup_databases(**kwargs)
