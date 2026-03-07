from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
import os
from hubspot import HubSpot
from simple_salesforce import Salesforce

class CRMAdapter(ABC):
    @abstractmethod
    async def push_lead(self, lead_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def get_contact(self, email: str) -> Dict[str, Any]:
        pass

class HubSpotAdapter(CRMAdapter):
    def __init__(self, access_token: str):
        self.client = HubSpot(access_token=access_token)

    async def push_lead(self, lead_data: Dict[str, Any]) -> bool:
        try:
            properties = {
                "email": lead_data.get("email"),
                "firstname": lead_data.get("first_name"),
                "lastname": lead_data.get("last_name"),
                "company": lead_data.get("company"),
                "jobtitle": lead_data.get("title")
            }
            self.client.crm.contacts.basic_api.create(simple_public_object_input_for_create=properties)
            return True
        except Exception as e:
            logging.error(f"HubSpot Error: {e}")
            return False

    async def get_contact(self, email: str) -> Dict[str, Any]:
        try:
            contact = self.client.crm.contacts.basic_api.get_by_id(contact_id=email, id_property="email")
            return contact.to_dict()
        except Exception:
            return None

class SalesforceAdapter(CRMAdapter):
    def __init__(self, access_token: str, instance_url: str):
        self.sf = Salesforce(instance_url=instance_url, session_id=access_token)

    async def push_lead(self, lead_data: Dict[str, Any]) -> bool:
        try:
            self.sf.Lead.create({
                'FirstName': lead_data.get('first_name'),
                'LastName': lead_data.get('last_name'),
                'Email': lead_data.get('email'),
                'Company': lead_data.get('company'),
                'Title': lead_data.get('title')
            })
            return True
        except Exception as e:
            logging.error(f"Salesforce Error: {e}")
            return False

    async def get_contact(self, email: str) -> Dict[str, Any]:
        try:
            results = self.sf.query(f"SELECT Id, Name, Email FROM Lead WHERE Email = '{email}'")
            return results['records'][0] if results['totalSize'] > 0 else None
        except Exception:
            return None

def get_crm_adapter(crm_type: str, config: Dict[str, Any]) -> CRMAdapter:
    """
    Factory to get the correct CRM adapter based on organization config.
    """
    if crm_type.lower() == "hubspot":
        return HubSpotAdapter(config.get("access_token"))
    elif crm_type.lower() == "salesforce":
        return SalesforceAdapter(config.get("access_token"), config.get("instance_url"))
    else:
        raise ValueError(f"Unsupported CRM: {crm_type}")
