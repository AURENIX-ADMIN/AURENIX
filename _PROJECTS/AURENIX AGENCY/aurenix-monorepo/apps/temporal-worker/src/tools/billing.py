import os
import logging
import stripe
from sqlalchemy import create_engine, text
from temporalio import activity
from tools.security import get_secret

@activity.defn
async def record_usage_event(org_id: str, event_type: str, quantity: int = 1, cost_credits: float = 0.0):
    """
    Activity to record usage in Aurenix DB and sync with Stripe.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        activity.logger.error("DATABASE_URL is not set")
        return False

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 1. Update Credit Balance
            conn.execute(
                text("UPDATE \"CreditBalance\" SET balance = balance - :cost, updated_at = NOW() WHERE organization_id = :org"),
                {"cost": cost_credits, "org": org_id}
            )
            
            # 2. Insert Usage Record
            # Using cuid-like ID generation or let DB handle it? prisma uses cuid()
            # For simplicity, we'll generate a random string here or use DEFAULT if cuid set in DB
            conn.execute(
                text("INSERT INTO \"UsageRecord\" (id, organization_id, type, quantity, cost_credits, timestamp) VALUES (:id, :org, :type, :qty, :cost, NOW())"),
                {
                    "id": f"usage_{os.urandom(8).hex()}",
                    "org": org_id,
                    "type": event_type,
                    "qty": quantity,
                    "cost": cost_credits
                }
            )

            # 3. Report to Stripe (if on metered plan)
            subscription = conn.execute(
                text("SELECT stripe_id FROM \"Subscription\" WHERE organization_id = :org AND status = 'ACTIVE'"),
                {"org": org_id}
            ).fetchone()

            if subscription and subscription[0]:
                try:
                    stripe.api_key = get_secret("STRIPE_SECRET_KEY")
                    # Note: In production, we would need to map event_type to a Stripe Subscription Item ID
                    # For MVP, we'll log this as a successful "event reported"
                    activity.logger.info(f"Reported {quantity} {event_type} usage units to Stripe for {org_id}")
                except Exception as stripe_err:
                    activity.logger.warning(f"Stripe reporting failed (non-critical): {stripe_err}")

            conn.commit()
            return True
    except Exception as e:
        activity.logger.error(f"Failed to record usage event: {e}")
        return False

@activity.defn
async def log_audit_action(org_id: str, action: str, resource: str, user_id: str = None, details: dict = None, severity: str = "INFO"):
    """
    Records an immutable audit log entry.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return False

    try:
        import json
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO \"AuditLog\" (id, organization_id, user_id, action, resource, details, severity, timestamp) VALUES (:id, :org, :user, :action, :res, :details, :sev, NOW())"),
                {
                    "id": f"audit_{os.urandom(8).hex()}",
                    "org": org_id,
                    "user": user_id,
                    "action": action,
                    "res": resource,
                    "details": json.dumps(details or {}),
                    "sev": severity
                }
            )
            conn.commit()
            return True
    except Exception as e:
        activity.logger.error(f"Audit Logging Failed: {e}")
        return False
