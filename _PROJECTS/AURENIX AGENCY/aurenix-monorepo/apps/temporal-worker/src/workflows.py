from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy


# Placeholder activity definition
@workflow.defn
class EmailProcessingWorkflow:
    def __init__(self):
        self.user_approved = False
        self.approval_decision = ""
        self.rejection_reason = ""

    @workflow.signal
    def approve_signal(self, decision: str, reason: str = ""):
        self.user_approved = True
        self.approval_decision = decision
        self.rejection_reason = reason

    @workflow.run
    async def run(self, email_input: dict):
        retry_policy = RetryPolicy(maximum_attempts=3)
        activity_timeout = timedelta(minutes=5)

        # 1. Classify
        intent = await workflow.execute_activity(
            "classify_email",
            args=[email_input["subject"], email_input["body"]],
            start_to_close_timeout=activity_timeout,
            retry_policy=retry_policy
        )

        if intent["category"] == "Noise":
            return "Ignored as Noise"

        # 2. Draft (Loop for corrections)
        draft = await workflow.execute_activity(
            "draft_response",
            args=[intent, []],
            start_to_close_timeout=activity_timeout
        )

        # 3. Wait for Approval (The Shield)
        # In a real app, we would notify the user here (e.g. via DB update/websocket)
        
        await workflow.wait_condition(lambda: self.user_approved)

        if self.approval_decision == "REJECT":
            return f"Draft Rejected: {self.rejection_reason}"
        
        # 4. Send
        await workflow.execute_activity(
            "send_email",
            args=[draft, email_input["sender"]],
            start_to_close_timeout=activity_timeout
        )

        return "Email Sent"

@workflow.defn
class MeetingObserverWorkflow:
    @workflow.run
    async def run(self, meeting_url: str, bot_name: str):
        activity_timeout = timedelta(minutes=5)
        # 1-hour timeout for meeting monitoring loop intervals
        monitor_timeout = timedelta(hours=2) 

        # 1. Dispatch Bot
        bot_info = await workflow.execute_activity(
            "dispatch_meeting_bot",
            args=[meeting_url, bot_name],
            start_to_close_timeout=activity_timeout
        )
        bot_id = bot_info["id"]

        # 2. Monitor Meeting (Polling loop)
        while True:
            status = await workflow.execute_activity(
                "check_bot_status",
                args=[bot_id],
                start_to_close_timeout=activity_timeout
            )
            
            if status["status_code"] == "meeting_done": # Hypothetical status
                break
            
            # Wait 60 seconds before checking again
            await workflow.sleep(60)

        # 3. Process Recording
        transcript = await workflow.execute_activity(
            "fetch_transcript",
            args=[bot_id],
            start_to_close_timeout=activity_timeout
        )

        # 4. Extract Insights
        insights = await workflow.execute_activity(
            "extract_meeting_insights",
            args=[transcript],
            start_to_close_timeout=activity_timeout
        )

        return insights

@workflow.defn
class LeadHunterWorkflow:
    """
    Workflow to find and qualify business leads using browser automation and AI.
    """
    @workflow.run
    async def run(self, config: dict):
        # config example: { "industries": ["SAAS", "AI"], "location": "USA", "min_employees": 50 }
        
        # 🛡️ Robust Retry Policies
        # Browsing activities are flaky by nature. We use exponential backoff.
        browser_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=5),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(minutes=5),
            maximum_attempts=5,
            non_retryable_error_types=["InvalidTargetError"]
        )
        
        db_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_attempts=3
        )

        activity_timeout = timedelta(minutes=15)

        try:
            # 1. Scrape Sources
            print(f"Workflow: Starting Lead Hunter for {config.get('industries')}")
            raw_leads = await workflow.execute_activity(
                "scrape_lead_sources",
                args=[config],
                start_to_close_timeout=activity_timeout,
                retry_policy=browser_retry_policy
            )

            # 2. Qualify and Enrich with AI
            qualified_leads = await workflow.execute_activity(
                "qualify_and_enrich_leads",
                args=[raw_leads, config.get("icp_description", "")],
                start_to_close_timeout=activity_timeout,
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            # 3. Save to Database
            saved_count = await workflow.execute_activity(
                "save_leads_to_db",
                args=[qualified_leads, config.get("organization_id")],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=db_retry_policy
            )

            # 4. Record Telemetry (ROI Calculation)
            await workflow.execute_activity(
                "record_lead_gen_telemetry",
                args=[{
                    "org_id": config.get("organization_id"),
                    "leads_found": len(raw_leads),
                    "leads_qualified": len(qualified_leads),
                    "saved_count": saved_count
                }],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=db_retry_policy
            )

            return {
                "status": "COMPLETED",
                "leads_found": len(raw_leads),
                "leads_qualified": len(qualified_leads),
                "saved_count": saved_count
            }

        except Exception as e:
            # 🚨 Alert on Critical Failure
            await workflow.execute_activity(
                "send_critical_alert",
                args=[{
                    "workflow": "LeadHunterWorkflow",
                    "org_id": config.get("organization_id"),
                    "error": str(e)
                }],
                start_to_close_timeout=timedelta(minutes=1)
            )
            raise e

@workflow.defn
class DocumentIntelligenceWorkflow:
    """
    Workflow to process documents (VANTAGE), extract insights, and index for RAG.
    """
    @workflow.run
    async def run(self, config: dict):
        # config example: { "resource_id": "...", "file_url": "...", "org_id": "..." }
        
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=5),
            maximum_attempts=3
        )
        
        resource_id = config.get("resource_id")
        
        try:
            # 1. Update Status to PROCESSING
            await workflow.execute_activity(
                "update_resource_status",
                args=[resource_id, "PROCESSING"],
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=retry_policy
            )

            # 2. Extract and Analyze (Vantage Intelligence)
            # Uses Multimodal LLM to "read" the document
            insights = await workflow.execute_activity(
                "process_document_vantage",
                args=[config],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )

            # 3. Store Insights in DB
            await workflow.execute_activity(
                "save_document_insights",
                args=[resource_id, insights],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            # 4. Index for RAG (Future step: Embeddings)
            await workflow.execute_activity(
                "index_document_knowledge",
                args=[resource_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            # 5. Final Status: INDEXED
            await workflow.execute_activity(
                "update_resource_status",
                args=[resource_id, "INDEXED"],
                start_to_close_timeout=timedelta(minutes=1)
            )

            return {"status": "SUCCESS", "resource_id": resource_id}

        except Exception as e:
            await workflow.execute_activity(
                "update_resource_status",
                args=[resource_id, "ERROR"],
                start_to_close_timeout=timedelta(minutes=1)
            )
            # Alert on failure
            await workflow.execute_activity(
                "send_critical_alert",
                args=[{
                    "workflow": "DocumentIntelligenceWorkflow",
                    "resource_id": resource_id,
                    "error": str(e)
                }],
                start_to_close_timeout=timedelta(minutes=1)
            )
            raise e
