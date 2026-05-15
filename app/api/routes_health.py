"""Health check routes."""

from fastapi import APIRouter

from app import APP_VERSION, SERVICE_NAME

router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    """Return service health metadata for load balancers and smoke tests."""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": APP_VERSION,
    }
