"""
AURENIX E2E SYSTEM TEST - "THE FINAL GATEKEEPER"
------------------------------------------------
Comprehensive validation of:
1. Intent Routing (Orchestrator)
2. Telemetry Persistence (Multi-tenant)
3. ROI Calculation (Business Logic)
4. Data Isolation (Privacy)
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Ensure we can import aurenix_core
sys.path.append(os.path.abspath("proyecto/MIGRACION-COMPLETA"))

from aurenix_core.telemetry.task_tracker import TaskTracker, TaskOutcome, TaskType
from aurenix_core.telemetry.storage import MemoryStorageAdapter
from aurenix_core.agents.orchestrator import AgentOrchestrator, IntentCategory
from aurenix_core.agents.sales_agent.sales_tools import SalesTools

async def run_e2e_test():
    print("🚀 [1/5] Initializing Aurenix Infrastructure...")
    
    # Setup Storage & Discovery
    storage = MemoryStorageAdapter()
    tracker = TaskTracker(storage=storage)
    
    # Setup Tools Registry
    tools = {
        "calculate_lead_roi": SalesTools.calculate_lead_roi,
        "generate_proposal": SalesTools.generate_proposal_markdown,
        "send_email": lambda **kwargs: {"status": "sent", "to": kwargs.get("to")},
    }
    
    orchestrator = AgentOrchestrator(available_tools=tools)
    
    print("🔒 [2/5] Validating Multi-tenant Isolation...")
    
    # Client A Operatons
    client_a_id = "ORG_TESLA"
    user_a = "elon@tesla.com"
    
    # Start task for Client A
    session_a = await tracker.start_task(user_a, TaskType.CODE_GENERATION, organization_id=client_a_id)
    await asyncio.sleep(0.1)
    await tracker.end_task(session_a.session_id, TaskOutcome.COMPLETED)
    
    # Client B Operations
    client_b_id = "ORG_SPACEX"
    user_b = "gwynne@spacex.com"
    
    session_b = await tracker.start_task(user_b, TaskType.RESEARCH, organization_id=client_b_id)
    await tracker.end_task(session_b.session_id, TaskOutcome.COMPLETED)
    
    # Verify Isolation
    roi_a = await tracker.get_organization_roi(client_a_id)
    roi_b = await tracker.get_organization_roi(client_b_id)
    
    assert roi_a["total_tasks"] == 1, "Client A data corrupted"
    assert roi_b["total_tasks"] == 1, "Client B data corrupted"
    print("✅ Multi-tenancy integrity verified.")

    print("🧠 [3/5] Validating Intelligent Orchestration (Fenix)...")
    
    # Test Sales Intent
    sales_msg = "Please calculate ROI for a team of 100 people with 80k salary and generate a proposal."
    classification = orchestrator.classify_intent(sales_msg)
    
    assert classification.category == IntentCategory.SALES
    assert "calculate_lead_roi" in classification.suggested_tools
    print("✅ Intent classification verified.")

    # Execute Sales Flow
    tool_args = {
        "num_employees": 100,
        "avg_annual_salary": 80000.0,
        "automation_potential_pct": 30.0
    }
    
    result = await orchestrator.execute_tool("calculate_lead_roi", tool_args, user_id=user_a)
    assert result.success is True
    assert result.result["projected_annual_savings_usd"] > 1000000
    print(f"✅ Sales ROI Calculation verified: ${result.result['projected_annual_savings_usd']:,} saved/year.")

    print("📊 [4/5] Validating Telemetry & Reporting logic...")
    
    summary = await tracker.get_user_summary(user_a)
    assert summary["total_tasks"] >= 1
    assert summary["success_rate"] == 100.0
    print(f"✅ User Summary verified for {user_a}.")

    print("🏁 [5/5] Final System State Check...")
    
    all_metrics = await storage.get_all_metrics()
    assert len(all_metrics) >= 2
    print(f"✅ Total of {len(all_metrics)} metrics persisted in 'The Source of Truth'.")
    
    print("\n" + "="*50)
    print("🏆 AURENIX ZERO-DEFECT E2E TEST PASSED")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
