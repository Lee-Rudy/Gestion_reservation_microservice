from fastapi import APIRouter, Query

from reservation_service.infrastructure.logs.logs_repository import LogsRepository

router = APIRouter(tags=["Logs"])


@router.get("/logs")
def get_logs(limit: int = Query(50, ge=1, le=1000)):
    repo = LogsRepository()
    logs = repo.get_recent_logs(limit)
    return logs
