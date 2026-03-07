from typing import Dict, Optional

# Elite Prompt Management: Prompt Registry
# This allows decoupled management of AI instructions.

PROMPT_COLLECTION = {
    "report_draft": {
        "system": "You are a World-Class Business Analyst for Aurenix Agency.",
        "template": "Analyze the following topic and provide a premium executive report: {topic}\n\nContext: {context}"
    },
    "lead_qualification": {
        "system": "You are an Elite Sales Strategist for Aurenix Agency.",
        "template": "Qualify this lead based on the following interactions: {interactions}\n\nDecision Matrix: {criteria}"
    },
    "email_summary": {
        "system": "You are a professional administrative assistant.",
        "template": "Summarize this email thread for a high-ticket executive: {content}"
    }
}

def get_prompt(prompt_id: str) -> Optional[Dict[str, str]]:
    return PROMPT_COLLECTION.get(prompt_id)
