import os
import logging
from typing import List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from temporalio import activity

# Configuration for Vertex AI Search
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "aurenix-dev")
LOCATION = "global" # Discovery Engine default is global
DATA_STORE_ID = os.getenv("VERTEX_SEARCH_DATA_STORE_ID", "aurenix-knowledge")

@activity.defn
async def search_internal_knowledge(
    query: str, 
    project_id: Optional[str] = None, 
    data_store_id: Optional[str] = None
) -> List[str]:
    target_project = project_id or PROJECT_ID
    target_store = data_store_id or DATA_STORE_ID
    
    activity.logger.info(f"Querying Vertex AI Search (Project: {target_project}, Store: {target_store}) for: {query}")
    
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        activity.logger.warning("GOOGLE_APPLICATION_CREDENTIALS missing, returning mock data")
        return [
            f"[MOCK] {target_store}: Aurenix standard operating procedure involves...",
            f"[MOCK] {target_store}: Client history for personalized stack..."
        ]

    try:
        client = discoveryengine.SearchServiceClient()
        
        serving_config = client.serving_config_path(
            project=target_project,
            location=LOCATION,
            data_store=target_store,
            serving_config="default_search",
        )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=5,
        )

        response = client.search(request)
        
        results = []
        for result in response.results:
            doc = result.document
            # Handle both snippet and direct data extraction
            snippets = doc.derived_struct_data.get('snippets', [])
            if snippets:
                results.append(str(snippets[0].get('snippet', snippets[0])))
            else:
                results.append(str(doc.derived_struct_data.get('text', str(doc))))
            
        return results if results else ["No relevant knowledge found in Vertex AI Search."]
        
    except Exception as e:
        activity.logger.error(f"Vertex AI Search Error: {e}")
        return [f"Error querying knowledge base ({target_store}): {e}"]
