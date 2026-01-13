"""
Verdic Guard Python SDK

A minimal SDK for validating outputs against execution contracts using the Verdic Guard API.
"""

import requests
from typing import Dict, Any, Optional


def validate(
    api_url: str,
    execution_config: Dict[str, Any],
    output: str
) -> Dict[str, Any]:
    """
    Validate output against an execution contract.
    
    Args:
        api_url: Verdic Guard API URL (e.g., "https://verdic.dev")
        execution_config: Execution contract dictionary containing validation rules
        output: Output string to validate
        
    Returns:
        Validation result dictionary with one of the following structures:
        - {"status": "OK", "drift": float, "output": str}
        - {"status": "BLOCKED", "reason": str, "detail": str, "hint": str (optional)}
        - {"status": "FAILED", "message": str}
        
    Raises:
        requests.RequestException: If network error occurs
        requests.HTTPError: If API request fails with HTTP error
    """
    try:
        response = requests.post(
            f"{api_url}/api/guard/validate",
            json={
                "executionConfig": execution_config,
                "output": output
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        # Re-raise network and HTTP errors for caller to handle
        raise
