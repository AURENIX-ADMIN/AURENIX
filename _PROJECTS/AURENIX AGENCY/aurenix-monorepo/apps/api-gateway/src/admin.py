from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from temporalio.client import Client

router = APIRouter(prefix="/admin", tags=["admin"])

# Mock DB for budget
# In reality, this would query the Postgres database
BUDGET_LIMITS = {
    "org_123": 100.00 # $100 limit
}
CURRENT_USAGE = {
    "org_123": 50.00 # $50 used
}

class KillWorkflowRequest(BaseModel):
    workflow_id: str
    run_id: Optional[str] = None
    reason: str = "Administrative Kill Switch activated"

class BudgetCheckRequest(BaseModel):
    organization_id: str
    estimated_cost: float

@router.post("/kill-workflow")
async def kill_workflow(request: KillWorkflowRequest):
    try:
        # Connect to Temporal
        # client = await Client.connect("temporal-server:7233")
        # await client.get_workflow_handle(request.workflow_id, run_id=request.run_id).terminate(request.reason)
        
        # Mocking success for MVP
        print(f"Terminating workflow {request.workflow_id} reason: {request.reason}")
        return {"status": "terminated", "workflow_id": request.workflow_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-budget")
async def check_budget(request: BudgetCheckRequest):
    limit = BUDGET_LIMITS.get(request.organization_id, 0)
    usage = CURRENT_USAGE.get(request.organization_id, 0)
    
    if usage + request.estimated_cost > limit:
        raise HTTPException(status_code=402, detail="Budget Exceeded")
    
    return {"status": "approved", "remaining": limit - usage}
