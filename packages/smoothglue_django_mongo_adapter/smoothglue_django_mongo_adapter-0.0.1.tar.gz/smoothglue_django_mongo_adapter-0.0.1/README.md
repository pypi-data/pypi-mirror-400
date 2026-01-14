# Django Mongo Adapter

A lightweight adapter that bridges the gap between **Django** and **MongoDB** (via MongoEngine). It provides utilities to seamlessly integrate MongoDB documents into the Django Admin, simplifies connection management, offers a pre-configured test runner for mocking MongoDB, and includes mixins for standardized audit trails.

## Features

- **Automatic Connection Management**: Configures `mongoengine` connections via Django settings.
- **Django Admin Integration**: View and filter MongoDB documents in the Django Admin as if they were SQL models.
- **Generic Wrappers**: Utilities to make Mongo QuerySets behave like Django QuerySets (great for generic views).
- **Test Runner**: A drop-in `MongoMockTestRunner` that ensures your tests never hit a real database.
- **Audit Mixins**: Standardized `created_at`, `updated_at`, and user tracking for Mongo documents.
- **Direct Imports**: Import common MongoEngine components (`Document`, `fields`, `mock_mongo_connection`) directly from the package.

## Installation

1.  Install the package:

    ```bash
    pip install smoothglue-django-mongo-adapter
    ```

2.  Add it to your `INSTALLED_APPS` in `settings.py`:
    ```python
    INSTALLED_APPS = [
        # ...
        "smoothglue.django_mongo_adapter",
    ]
    ```

## Configuration

Define your MongoDB connection settings in `settings.py`. The adapter will automatically initialize the connection on startup.

```python
MONGO_CLIENT_CONNECTION = {
    "alias": "default",
    "host": "mongodb://localhost:27017/my_database",
    # "username": "root",
    # "password": "password",
}
```

## Usage

### 1. Django Admin Integration

To display a MongoDB document in the Django Admin, you need two things:

1.  The **MongoEngine Document** (your actual data).
2.  A **Django Proxy Model** (to tell Django Admin what fields to display).

**models.py**:

```python
from django.db import models
from mongoengine import Document, StringField

# 1. The Mongo Document
class MyLog(Document):
    message = StringField()
    level = StringField()

# 2. The Django Proxy Model
class MyLogAdminView(models.Model):
    id = models.UUIDField(primary_key=True)
    message = models.CharField(max_length=255)
    level = models.CharField(max_length=50)

    class Meta:
        managed = False  # Crucial: tells Django not to create a table
        verbose_name = "System Log"
```

**admin.py**:
Inherit from `MongoModelAdmin` and set the `mongo_document` attribute.

```python
from django.contrib import admin
from smoothglue.django_mongo_adapter.utils import MongoModelAdmin
from .models import MyLog, MyLogAdminView

@admin.register(MyLogAdminView)
class MyLogAdmin(MongoModelAdmin):
    mongo_document = MyLog
    list_display = ("message", "level")

    # Optional: Map Django field names to Mongo fields/paths
    mongo_mapper = {
        "django_field_name": "mongo.field.path"
    }
```

### 2. Custom Views

If you need to pass MongoDB data to a Django Generic View (like `ListView`), use the `AutoMongoQuerySetWrapper`:

```python
from django.views.generic import ListView
from smoothglue.django_mongo_adapter.utils import AutoMongoQuerySetWrapper
from .models import MyLog, MyLogAdminView

class LogListView(ListView):
    template_name = "logs.html"

    def get_queryset(self):
        # Wraps the Mongo QuerySet so it behaves like a Django QuerySet
        return AutoMongoQuerySetWrapper(MyLog.objects.all(), MyLogAdminView)
```

### 3. Testing

Use the provided test runner to automatically mock MongoDB connections using `mongomock`.

**settings.py**:

```python
TEST_RUNNER = "smoothglue.django_mongo_adapter.test_runner.MongoMockTestRunner"

MONGO_DATABASES = {
    "test": {"db": "mongo-test-db"}
}
```

### 4. Audit Mixins

Easily add audit fields to your Mongo documents.

```python
from smoothglue.django_mongo_adapter import Document, fields, MongoTimeAuditDocument, MongoUserAuditDocument

class MyDocument(MongoTimeAuditDocument, MongoUserAuditDocument, Document):
    name = fields.StringField()

    # Automatically has:
    # - created_at (datetime)
    # - updated_at (datetime)
    # - created_by (property, links to Django User)
    # - updated_by (property, links to Django User)
```

To set the user:

```python
doc = MyDocument(name="Test")
doc.created_by = request.user
doc.save()
```

### 5. Utilities

You can use `mock_mongo_connection` to patch MongoEngine connection in your tests without importing `mongoengine` or `mongomock` directly:

```python
from smoothglue.django_mongo_adapter import mock_mongo_connection

@mock_mongo_connection()
class MyTest(unittest.TestCase):
    # ...
```
