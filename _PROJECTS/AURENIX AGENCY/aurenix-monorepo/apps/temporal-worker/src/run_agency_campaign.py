
import asyncio
import os
import uuid
from temporalio.client import Client

async def run_campaign():
    print("--- [AURENIX] Launching 'The Agency' Self-Lead Gen Campaign ---")
    
    # 1. Connect to Temporal
    # Ensure this matches your local or docker setting. 
    # Since we run outside docker, localhost:7233 is correct.
    client = await Client.connect("localhost:7233")
    
    # 2. Campaign Configuration
    # We are the client. We want leads for OUR agency.
    agency_config = {
        "industries": ["E-commerce", "Fashion Retail", "Consumer Goods"],
        "location": "Spain",
        "icp_description": "Mid-sized e-commerce brands in Spain (Madrid, Barcelona) likely to need AI automation for customer support or marketing. Revenue > $1M if visible.",
        "organization_id": "aurenix-agency-hq", # Self-reference
        "max_leads": 5 # Limit for test run
    }
    
    workflow_id = f"agency-campaign-{uuid.uuid4()}"
    
    print(f"Starting Workflow {workflow_id}...")
    print(f"Targeting: {agency_config['industries']} in {agency_config['location']}")
    
    # 3. Start Workflow
    handle = await client.start_workflow(
        "LeadHunterWorkflow",
        args=[agency_config],
        id=workflow_id,
        task_queue="fenix-queue-local",
        run_timeout=None # Let it run
    )
    
    print(f"Workflow started. Run ID: {handle.run_id}")
    print("Waiting for results (this involves real browsing)...")
    
    # 4. Wait for Result
    result = await handle.result()
    
    print("\n--- [CAMPAIGN COMPLETE] ---")
    print("Status:", result.get("status"))
    print("Leads Found:", result.get("leads_found"))
    print("Leads Qualified:", result.get("leads_qualified"))
    print("Saved to DB:", result.get("saved_count"))
    print("---------------------------")

if __name__ == "__main__":
    asyncio.run(run_campaign())
