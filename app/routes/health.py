from fastapi import APIRouter

from schemas import SimpleHealthResponse
from services.health_checker import HealthChecker, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=SimpleHealthResponse)
async def health() -> SimpleHealthResponse:
    return SimpleHealthResponse(status="ok")


@router.get("/rabbitmq", response_model=HealthResponse)
async def health_rabbitmq() -> HealthResponse:
    return HealthChecker.rabbit()


@router.get("/mongodb", response_model=HealthResponse)
async def health_mongodb() -> HealthResponse:
    return HealthChecker.mongo()
