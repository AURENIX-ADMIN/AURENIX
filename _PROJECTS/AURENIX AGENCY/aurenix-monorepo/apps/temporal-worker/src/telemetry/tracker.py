import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import structlog
from .models import TaskType, TaskOutcome, TaskMetrics
from .productivity import ProductivityCalculator

logger = structlog.get_logger()

class TaskTracker:
    def __init__(self):
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    async def start_task(
        self,
        user_id: str,
        task_type: TaskType,
        organization_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        session_id = str(uuid.uuid4())
        self._active_sessions[session_id] = {
            "user_id": user_id,
            "organization_id": organization_id,
            "task_type": task_type,
            "started_at": datetime.now(timezone.utc),
            "metadata": metadata or {}
        }
        
        logger.info("telemetry_task_started", session_id=session_id, task_type=task_type)
        return session_id

    async def end_task(
        self,
        session_id: str,
        outcome: TaskOutcome,
        cost_usd: Optional[float] = None
    ) -> Optional[TaskMetrics]:
        session = self._active_sessions.pop(session_id, None)
        if not session:
            logger.warning("telemetry_session_not_found", session_id=session_id)
            return None

        ended_at = datetime.now(timezone.utc)
        duration_ms = int((ended_at - session["started_at"]).total_seconds() * 1000)
        
        metrics = ProductivityCalculator.calculate_metrics(
            session_id=session_id,
            user_id=session["user_id"],
            organization_id=session["organization_id"],
            task_type=session["task_type"],
            duration_ms=duration_ms,
            outcome=outcome,
            cost_usd=cost_usd
        )
        
        logger.info("telemetry_task_ended", 
                    session_id=session_id, 
                    duration_ms=duration_ms, 
                    time_saved_ms=metrics.time_saved_ms)
        
        # Note: Porting to Database would happen here
        return metrics
