from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class TaskType(str, Enum):
    EMAIL_COMPOSE = "email_compose"
    EMAIL_REPLY = "email_reply"
    DOCUMENT_SUMMARY = "document_summary"
    DATA_EXTRACTION = "data_extraction"
    CALENDAR_SCHEDULING = "calendar_scheduling"
    RESEARCH = "research"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    GENERAL_QUERY = "general_query"
    WORKFLOW_AUTOMATION = "workflow_automation"

class TaskOutcome(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REQUIRES_HUMAN = "requires_human"

class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

class TaskMetrics(BaseModel):
    session_id: str
    user_id: str
    organization_id: Optional[str] = None
    task_type: TaskType
    duration_ms: int
    estimated_manual_time_ms: int
    time_saved_ms: int
    time_saved_percentage: float
    outcome: TaskOutcome
    cost_usd: Optional[float] = None
