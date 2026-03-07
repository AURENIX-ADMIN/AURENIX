import os
from typing import Optional
from pydantic import BaseModel

class ClientConfig(BaseModel):
    organization_id: str
    external_db_uri: Optional[str] = None
    gcp_project_id: Optional[str] = None
    vertex_data_store_id: Optional[str] = None
    client_email: Optional[str] = None
    auto_approve: bool = False

from tools.security import decrypt_secret

async def get_client_config(organization_id: str) -> ClientConfig:
    """
    Retrieves and decrypts the configuration for a specific organization.
    """
    # Mock logic for MVP verification with elite security
    if organization_id == "demo-org":
        encrypted_db_uri = os.getenv("EXTERNAL_DATABASE_URL_ENCRYPTED", "")
        
        return ClientConfig(
            organization_id=organization_id,
            gcp_project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            vertex_data_store_id=os.getenv("VERTEX_SEARCH_DATA_STORE_ID"),
            # Elite Level: Decrypt on the fly for activities
            external_db_uri=decrypt_secret(encrypted_db_uri) if encrypted_db_uri else os.getenv("EXTERNAL_DATABASE_URL"),
            auto_approve=False
        )
    
    return ClientConfig(organization_id=organization_id)
