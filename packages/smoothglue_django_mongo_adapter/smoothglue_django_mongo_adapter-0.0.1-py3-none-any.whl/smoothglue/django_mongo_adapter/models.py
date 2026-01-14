from django.contrib.auth import get_user_model
from django.utils import timezone
from mongoengine import Document, fields


class MongoTimeAuditDocument(Document):
    """
    An abstract MongoEngine document that tracks creation and modification times.
    """

    created_at = fields.DateTimeField(default=timezone.now)
    updated_at = fields.DateTimeField(default=timezone.now)

    meta = {"abstract": True}

    def clean(self):
        """
        Ensure updated_at is refreshed on save.
        """
        self.updated_at = timezone.now()
        super().clean()


class MongoUserAuditDocument(Document):
    """
    An abstract MongoEngine document that tracks the user who created and updated the record.
    Stores the Django User ID as a string.
    """

    dj_created_by_id = fields.StringField()
    dj_updated_by_id = fields.StringField()

    meta = {"abstract": True}

    @property
    def created_by(self):
        if self.dj_created_by_id:
            try:
                return get_user_model().objects.get(id=self.dj_created_by_id)
            except (get_user_model().DoesNotExist, ValueError):
                return None
        return None

    @created_by.setter
    def created_by(self, user):
        if user and hasattr(user, "id"):
            self.dj_created_by_id = str(user.id)
        else:
            self.dj_created_by_id = None

    @property
    def updated_by(self):
        if self.dj_updated_by_id:
            try:
                return get_user_model().objects.get(id=self.dj_updated_by_id)
            except (get_user_model().DoesNotExist, ValueError):
                return None
        return None

    @updated_by.setter
    def updated_by(self, user):
        if user and hasattr(user, "id"):
            self.dj_updated_by_id = str(user.id)
        else:
            self.dj_updated_by_id = None
