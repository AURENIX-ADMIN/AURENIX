import os
import logging
from google.cloud import secret_manager

# Elite Security: Google Secret Manager Integration
# Replaces manual AES-256-GCM

def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Retrieves a secret from Google Secret Manager.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT is not set in the environment.")

    client = secret_manager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    try:
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload
    except Exception as e:
        logging.error(f"Failed to access secret {secret_id}: {e}")
        raise e

def set_secret(secret_id: str, payload: str) -> str:
    """
    Creates or updates a secret in Google Secret Manager.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT is not set in the environment.")

    client = secret_manager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    try:
        # Check if secret exists
        try:
            client.get_secret(request={"name": f"{parent}/secrets/{secret_id}"})
        except Exception:
            # Create it if it doesn't exist
            client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )

        # Add a new version
        client.add_secret_version(
            request={
                "parent": f"{parent}/secrets/{secret_id}",
                "payload": {"data": payload.encode("UTF-8")},
            }
        )
        return f"Secret {secret_id} updated successfully."
    except Exception as e:
        logging.error(f"Failed to set secret {secret_id}: {e}")
        raise e

# Deprecated manual encryption functions
def encrypt_secret(plain_text: str) -> str:
    logging.warning("DEPRECATED: encrypt_secret (manual AES) is deprecated. Use GSM.")
    raise NotImplementedError("Manual AES encryption is disabled. Use Google Secret Manager.")

def decrypt_secret(encrypted_text: str) -> str:
    logging.warning("DEPRECATED: decrypt_secret (manual AES) is deprecated.")
    return "[MANUAL_ENCRYPTION_DEPRECATED_MIGRATE_TO_GSM]"
