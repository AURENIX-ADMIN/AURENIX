import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows and activities
from src.workflows import EmailProcessingWorkflow, MeetingObserverWorkflow, LeadHunterWorkflow, DocumentIntelligenceWorkflow
from src.interceptors import AuditInterceptor
from src.activities import (
    run_agent_reasoning_step,
    classify_email,
    draft_response,
    send_email,
    dispatch_meeting_bot,
    check_bot_status,
    fetch_transcript,
    extract_meeting_insights,
    find_available_slots,
    propose_times,
    reschedule_conflict,
    scrape_lead_sources,
    qualify_and_enrich_leads,
    save_leads_to_db,
    record_lead_gen_telemetry,
    send_critical_alert,
    update_resource_status,
    process_document_vantage,
    save_document_insights,
    index_document_knowledge
)

async def main():
    # 📝 Configure Structured Logging
    from src.logger_config import configure_logger
    configure_logger()

    # Connect to Temporal Server
    client = await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))

    # Create Worker
    worker = Worker(
        client,
        task_queue="fenix-queue-local",
        workflows=[EmailProcessingWorkflow, MeetingObserverWorkflow, LeadHunterWorkflow, DocumentIntelligenceWorkflow],
        interceptors=[AuditInterceptor()],
        activities=[
            run_agent_reasoning_step,
            classify_email,
            draft_response,
            send_email,
            dispatch_meeting_bot,
            check_bot_status,
            fetch_transcript,
            extract_meeting_insights,
            find_available_slots,
            propose_times,
            reschedule_conflict,
            scrape_lead_sources,
            qualify_and_enrich_leads,
            save_leads_to_db,
            record_lead_gen_telemetry,
            send_critical_alert,
            update_resource_status,
            process_document_vantage,
            save_document_insights,
            index_document_knowledge
        ],
    )

    print("Starting FENIX Temporal Worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
