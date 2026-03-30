from contextlib import asynccontextmanager

from fastapi import FastAPI
from mongoengine import connect

from config import settings
from routes import jobs_router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host=settings.mongo_uri)
    yield


app = FastAPI(title="Media Processing Pipeline", lifespan=lifespan)

# Include routers
app.include_router(jobs_router)
app.include_router(health_router)
