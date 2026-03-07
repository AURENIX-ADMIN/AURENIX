import json
from datetime import datetime
from typing import Any, Optional

from temporalio import activity
from temporalio.worker import ActivityInboundInterceptor, Interceptor
from src.telemetry.tracker import TaskTracker, TaskOutcome, TaskType
from src.logger_config import get_logger

# Professional Logging
logger = get_logger("audit")

# Global telemetry tracker
telemetry_tracker = TaskTracker()

# Mapping of activity names
ACTIVITY_TASK_MAP = {
    "scrape_lead_sources": TaskType.RESEARCH,
    "qualify_and_enrich_leads": TaskType.RESEARCH,
    "save_leads_to_db": TaskType.WORKFLOW_AUTOMATION,
    "record_lead_gen_telemetry": TaskType.WORKFLOW_AUTOMATION,
    "classify_email": TaskType.RESEARCH,
    "generate_draft": TaskType.EMAIL_COMPOSE,
}

class AuditInterceptor(Interceptor):
    def intercept_activity(
        self, next: ActivityInboundInterceptor
    ) -> ActivityInboundInterceptor:
        return AuditActivityInboundInterceptor(next)

class AuditActivityInboundInterceptor(ActivityInboundInterceptor):
    async def execute_activity(self, input: Any) -> Any:
        info = activity.info()
        activity_type = info.activity_type
        workflow_id = info.workflow_id
        
        start_time = datetime.now()
        
        # 🛡️ Multitenant context extraction
        # Try to find org_id in args if it's a dict
        org_id = "unknown"
        if input.args and isinstance(input.args[0], dict):
            org_id = input.args[0].get("organization_id", "unknown")

        # Telemetry Start
        task_type = ACTIVITY_TASK_MAP.get(activity_type, TaskType.WORKFLOW_AUTOMATION)
        telemetry_session_id = await telemetry_tracker.start_task(
            user_id="anonymous", 
            task_type=task_type,
            organization_id=org_id,
            metadata={"activity": activity_type, "workflow_id": workflow_id}
        )

        logger.info("activity_started", 
            activity=activity_type, 
            workflow_id=workflow_id,
            org_id=org_id,
            telemetry_id=telemetry_session_id
        )

        try:
            result = await self.next.execute_activity(input)
            
            # Telemetry End
            if telemetry_session_id:
                await telemetry_tracker.end_task(
                    telemetry_session_id, 
                    TaskOutcome.COMPLETED
                )

            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            logger.info("activity_completed", 
                activity=activity_type, 
                workflow_id=workflow_id,
                duration_ms=duration_ms,
                status="success"
            )
            return result
        except Exception as e:
            # Telemetry Failure
            if telemetry_session_id:
                await telemetry_tracker.end_task(
                    telemetry_session_id, 
                    TaskOutcome.FAILED
                )

            logger.error("activity_failed", 
                activity=activity_type, 
                workflow_id=workflow_id,
                error=str(e),
                status="failed"
            )
            raise e
