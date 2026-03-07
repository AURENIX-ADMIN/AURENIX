import httpx
import logging
from typing import Dict, Any, Optional, Union
from temporalio import activity

# Universal API Connector
# Supports REST/JSON integrations with any third-party service.

@activity.defn
async def call_external_api(
    url: str, 
    method: str = "GET", 
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Makes a professional HTTP call to a client or third-party service.
    """
    activity.logger.info(f"Calling API: {method} {url}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=payload,
                params=params
            )
            
            # Check for success
            response.raise_for_status()
            
            return {
                "status_code": response.status_code,
                "data": response.json() if "application/json" in response.headers.get("content-type", "") else response.text
            }
        except httpx.HTTPStatusError as e:
            activity.logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        except Exception as e:
            activity.logger.error(f"Generic API Error: {e}")
            return {"error": str(e)}
