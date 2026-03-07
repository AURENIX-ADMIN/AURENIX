from typing import Dict, List, Optional, Any
from .models import TaskType, ComplexityLevel, TaskMetrics, TaskOutcome

class TimeEstimator:
    # Base times in milliseconds
    BASE_TIMES = {
        TaskType.EMAIL_COMPOSE: 10 * 60 * 1000,
        TaskType.EMAIL_REPLY: 5 * 60 * 1000,
        TaskType.DOCUMENT_SUMMARY: 20 * 60 * 1000,
        TaskType.DATA_EXTRACTION: 30 * 60 * 1000,
        TaskType.CALENDAR_SCHEDULING: 3 * 60 * 1000,
        TaskType.RESEARCH: 45 * 60 * 1000,
        TaskType.CODE_GENERATION: 30 * 60 * 1000,
        TaskType.TRANSLATION: 15 * 60 * 1000,
        TaskType.GENERAL_QUERY: 5 * 60 * 1000,
        TaskType.WORKFLOW_AUTOMATION: 90 * 60 * 1000,
    }
    
    COMPLEXITY_MULTIPLIERS = {
        ComplexityLevel.SIMPLE: 0.5,
        ComplexityLevel.MODERATE: 1.0,
        ComplexityLevel.COMPLEX: 2.0,
        ComplexityLevel.EXPERT: 3.5,
    }
    
    @classmethod
    def estimate_manual_time(
        cls,
        task_type: TaskType,
        complexity: ComplexityLevel = ComplexityLevel.MODERATE,
        domain_factor: float = 1.0
    ) -> int:
        base_time = cls.BASE_TIMES.get(task_type, 10 * 60 * 1000)
        multiplier = cls.COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)
        return int(base_time * multiplier * domain_factor)

class ProductivityCalculator:
    @staticmethod
    def calculate_metrics(
        session_id: str,
        user_id: str,
        task_type: TaskType,
        duration_ms: int,
        outcome: TaskOutcome,
        organization_id: Optional[str] = None,
        complexity: ComplexityLevel = ComplexityLevel.MODERATE,
        cost_usd: Optional[float] = None
    ) -> TaskMetrics:
        estimated_manual_ms = TimeEstimator.estimate_manual_time(task_type, complexity)
        
        if outcome == TaskOutcome.COMPLETED:
            time_saved_ms = max(0, estimated_manual_ms - duration_ms)
        else:
            time_saved_ms = 0
            
        time_saved_pct = (time_saved_ms / estimated_manual_ms * 100) if estimated_manual_ms > 0 else 0
        
        return TaskMetrics(
            session_id=session_id,
            user_id=user_id,
            organization_id=organization_id,
            task_type=task_type,
            duration_ms=duration_ms,
            estimated_manual_time_ms=estimated_manual_ms,
            time_saved_ms=time_saved_ms,
            time_saved_percentage=round(time_saved_pct, 2),
            outcome=outcome,
            cost_usd=cost_usd
        )
