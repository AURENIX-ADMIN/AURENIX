from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI(title="FENIX API Gateway")

class GooglePubSubMessage(BaseModel):
    message: dict
    subscription: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

from redis import Redis
import os

# Initialize Redis client
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    try:
        # Google Pub/Sub pushes messages here
        body = await request.json()
        
        # Extract message ID for deduplication
        # Structure depends on Pub/Sub format, usually message.messageId
        message_id = body.get("message", {}).get("messageId")
        
        if message_id:
            # Check if processed
            if redis_client.set(f"gmail_event:{message_id}", "1", nx=True, ex=60):
                # New event
                print(f"Processing new Gmail event: {message_id}")
                # TODO: Trigger Temporal Workflow
            else:
                print(f"Duplicate Gmail event: {message_id}")
                return {"status": "duplicate"}
                
        return {"status": "received"}
    except Exception as e:
        print(f"Error processing Gmail webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/webhooks/outlook")
async def outlook_webhook(request: Request):
    # Retrieve validation token for setup
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain")
        
    try:
        body = await request.json()
        print(f"Received Outlook notification: {body}")
        # TODO: Process notification
        return {"status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing webhook")

from .admin import router as admin_router
app.include_router(admin_router)
