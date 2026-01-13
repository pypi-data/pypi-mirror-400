import os
import time
from typing import Dict, Any, List, Union
from flotorch.sdk.flotracer.manager import FloTorchTracingManager
from flotorch.sdk.flotracer.config import FloTorchFramework
from flotorch.sdk.utils.http_utils import http_get
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error

logger = get_logger()


def initialize_tracing_manager(base_url: str, api_key: str, tracer_config: Dict[str, Any], framework: FloTorchFramework):
    """Get initialized tracing manager"""
    try:
        if tracer_config is None:
            tracer_config = {}
        if tracer_config.get("enabled", False):
            tracer_config["base_url"] = base_url
            tracer_config["auth_token"] = api_key
            return FloTorchTracingManager(
                config=tracer_config,
                framework=framework
            )
    except Exception as e:
        # Graceful degradation - tracing fails, LLM continues to work
        print(f"Warning: LLM tracing initialization failed: {e}")
    return None


def fetch_traces_from_api(base_url: str, api_key: str, existing_tracer_ids: Union[set[str], list[str]] = None, additional_tracer_ids: Union[set[str], list[str], str] = None) -> List[Dict[str, Any]]:
    """
    Fetch traces from the API for the given tracer IDs.
    If additional_tracer_ids is provided, it will be added to the existing_tracer_ids.
    Args:
        tracer_ids: List of trace IDs to fetch
        base_url: Base URL for the API
        api_key: API key for authentication
            
    Returns:
        List of trace dictionaries from the API
        
    Raises:
        ValueError: If base_url or api_key is not provided
    """
    if not base_url:
        raise ValueError("base_url is required to fetch traces")
    
    if not api_key:
        raise ValueError("api_key is required to fetch traces")

    tracer_ids = set()
    if additional_tracer_ids and isinstance(additional_tracer_ids, str):
        additional_tracer_ids = [additional_tracer_ids]
    
    tracer_ids = tracer_ids.union(existing_tracer_ids or [], additional_tracer_ids or [])

    time.sleep(5) # Wait for the traces to be generated. Need to fix this
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    results = []
    
    # Iterate through each tracer_id and make API calls
    for tracer_id in tracer_ids:
        try:
            # Construct the API URL for each trace
            url = f"{base_url.rstrip('/')}/v1/traces/{tracer_id}"
            # Make the API call
            trace_data = http_get(url, headers=headers)
            results.append({"trace_id": tracer_id, "trace_data": trace_data, "status": "success"})

        except Exception as e:
            # Log the error but continue with other traces
            logger.error(Error(operation="fetch_traces_from_api",error=e))
            # Add None or error info to maintain list order
            results.append({"status": "failed", "error": str(e)[:100], "trace_id": tracer_id, "trace_data": None})
    
    return results
