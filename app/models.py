from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField, DictField


class Job(Document):
    meta = {
        "collection": "jobs",
        "indexes": ["status"],
    }

    status = StringField(
        required=True,
        default="pending",
        choices=["pending", "processing", "completed", "failed"],
    )
    file_name = StringField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    result = DictField()
    error = StringField()
