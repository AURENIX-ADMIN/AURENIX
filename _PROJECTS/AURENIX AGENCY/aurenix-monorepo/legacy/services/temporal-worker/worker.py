import asyncio
import logging
import json
import yaml
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from pydantic import BaseModel
from typing import Dict, Any, List

# --- Data Models ---
class WorkflowBlueprint(BaseModel):
    name: str
    version: str
    steps: List[Dict[str, Any]]

# --- Activities ---
@activity.defn
async def generic_activity(action: str, params: Dict[str, Any]) -> str:
    """
    A generic activity that can execute different logic based on 'action'.
    In a real implementation, this would dispatch to specific logic or external APIs.
    """
    logging.info(f"Executing action: {action} with params: {params}")
    
    if action == "log_message":
        return f"Logged: {params.get('message', 'No message')}"
    elif action == "http_get":
        # Placeholder for HTTP activity
        return f"GET request to {params.get('url')} successful (simulated)"
    
    return f"Action {action} processed."

# --- Workflows ---
@workflow.defn
class DynamicinterpreterWorkflow:
    @workflow.run
    async def run(self, blueprint_yaml: str, context_data: Dict[str, Any]) -> List[str]:
        """
        Dynamically executes a workflow based on a YAML blueprint.
        """
        blueprint_data = yaml.safe_load(blueprint_yaml)
        blueprint = WorkflowBlueprint(**blueprint_data)
        
        results = []
        workflow.logger.info(f"Starting workflow: {blueprint.name} v{blueprint.version}")

        for step in blueprint.steps:
            action = step.get("action")
            step_id = step.get("id")
            params = step.get("params", {})
            
            # Merit params with context
            # In a real engine, we'd use Jinja2 or similar for variable substitution
            
            result = await workflow.execute_activity(
                generic_activity,
                args=[action, params],
                start_to_close_timeout_seconds=60,
            )
            results.append(f"Step {step_id}: {result}")
        
        return results

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Connect to Temporal server (assuming local default for now)
    client = await Client.connect("localhost:7233")
    
    # Create worker
    worker = Worker(
        client,
        task_queue="aurenix-dynamic-queue",
        workflows=[DynamicinterpreterWorkflow],
        activities=[generic_activity],
    )
    
    print("Worker started. Listening on 'aurenix-dynamic-queue'.")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
