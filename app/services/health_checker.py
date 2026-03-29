from typing import Optional

import pika
from config import settings
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    error: Optional[str] = None
    collections: Optional[list[str]] = None


class HealthChecker:
    @staticmethod
    def rabbit() -> HealthResponse:
        try:
            params = pika.URLParameters(settings.rabbitmq_url)
            connection = pika.BlockingConnection(params)
            connection.close()
            return HealthResponse(status="healthy")
        except Exception as e:
            return HealthResponse(status="unhealthy", error=str(e))

    @staticmethod
    def mongo() -> HealthResponse:
        try:
            from mongoengine.connection import get_db
            db = get_db()
            collections = db.list_collection_names()
            return HealthResponse(status="healthy", collections=collections)
        except Exception as e:
            return HealthResponse(status="unhealthy", error=str(e))
