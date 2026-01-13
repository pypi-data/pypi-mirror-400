# Verdic Guard Python SDK

A minimal Python SDK for validating outputs against execution contracts using the Verdic Guard API.

## Installation

### Using pip

```bash
pip install verdic-guard
```

### From source

```bash
git clone https://github.com/verdic/verdic-guard-python.git
cd verdic-guard-python
pip install -r requirements.txt
python setup.py install
```

Or copy `verdic_guard.py` directly into your project (only requires `requests` library).

### New to Verdic Guard?

📚 **[Read the Quickstart Guide](../../SDK_QUICKSTART.md)** for a complete introduction to Verdic Guard and execution contracts.

## Quick Start

```python
from verdic_guard import validate

# Define your execution contract
execution_config = {
    "schemaVersion": "1.0.0",
    "globalIntent": "Provide medical information",
    "taskIntent": "Explain medication side effects",
    "stepIntent": "List common side effects",
    "domain": "medicine",
    "audience": "general_public",
    "allowCode": False,
    "allowExplanation": True,
    "allowActionableDetails": False,
    "executionThreshold": 0.3
}

# Validate an output
output = "Common side effects include nausea and headache."

try:
    result = validate(
        api_url="https://verdic.dev",
        execution_config=execution_config,
        output=output
    )
    
    if result["status"] == "OK":
        print("✓ Output validated successfully")
        print(f"  Drift: {result['drift']}")
    elif result["status"] == "BLOCKED":
        print(f"✗ Output blocked: {result['reason']}")
        print(f"  Detail: {result['detail']}")
        if "hint" in result:
            print(f"  Hint: {result['hint']}")
    elif result["status"] == "FAILED":
        print(f"✗ Validation failed: {result['message']}")
        
except Exception as e:
    print(f"Error: {e}")
```

## API Reference

### `validate(api_url, execution_config, output)`

Validates an output against an execution contract.

**Parameters:**

- `api_url` (str): The Verdic Guard API URL (e.g., "https://verdic.dev")
- `execution_config` (dict): Execution contract dictionary containing validation rules
- `output` (str): The output string to validate

**Returns:**

A dictionary with one of the following structures:

**Success (OK):**
```python
{
    "status": "OK",
    "drift": 0.15,  # float between 0 and 1
    "output": "validated output string"
}
```

**Blocked:**
```python
{
    "status": "BLOCKED",
    "reason": "MODALITY",  # or "DOMAIN_SAFETY" or "INTENT_DRIFT"
    "detail": "Detailed explanation of the violation",
    "hint": "Optional suggestion for remediation"
}
```

**Failed:**
```python
{
    "status": "FAILED",
    "message": "Error description"
}
```

**Raises:**

- `requests.RequestException`: If a network error occurs
- `requests.HTTPError`: If the API returns an HTTP error status

## ExecutionConfig Schema

The `execution_config` parameter should be a dictionary with the following structure:

```python
{
    "schemaVersion": "1.0.0",  # Required: Schema version
    
    # Intent hierarchy (all required)
    "globalIntent": "High-level purpose",
    "taskIntent": "Specific task being performed",
    "stepIntent": "Current step within the task",
    
    # Context (required)
    "domain": "software",  # software, medicine, chemistry, law, finance, education, general
    "audience": "professional",  # general_public, student, professional, researcher
    
    # Modality controls (optional, defaults shown)
    "allowCode": True,  # Whether code blocks are permitted
    "allowExplanation": True,  # Whether explanatory text is permitted
    "allowCreative": False,  # Whether creative/narrative content is permitted
    "allowActionableDetails": False,  # Whether domain-specific actionable details are permitted
    
    # Drift control (optional)
    "executionThreshold": 0.5,  # Drift threshold (0-1) above which output is blocked
    
    # Retry control (optional)
    "maxRetries": 0  # Maximum retry attempts (informational only)
}
```

## Examples

### Software Development

```python
from verdic_guard import validate

result = validate(
    api_url="https://verdic.dev",
    execution_config={
        "schemaVersion": "1.0.0",
        "globalIntent": "Provide software development assistance",
        "taskIntent": "Generate API endpoint code",
        "stepIntent": "Create Express route handler",
        "domain": "software",
        "audience": "professional",
        "allowCode": True,
        "allowExplanation": True,
        "executionThreshold": 0.5
    },
    output="const handler = (req, res) => { res.json({ status: 'ok' }); }"
)
```

### Medical Information

```python
from verdic_guard import validate

result = validate(
    api_url="https://verdic.dev",
    execution_config={
        "schemaVersion": "1.0.0",
        "globalIntent": "Provide medical information",
        "taskIntent": "Explain medication side effects",
        "stepIntent": "List common side effects",
        "domain": "medicine",
        "audience": "general_public",
        "allowCode": False,
        "allowExplanation": True,
        "allowActionableDetails": False,
        "executionThreshold": 0.3
    },
    output="Common side effects include nausea and headache."
)
```

## Error Handling

The SDK raises standard `requests` library exceptions:

```python
from verdic_guard import validate
import requests

try:
    result = validate(api_url, execution_config, output)
except requests.ConnectionError:
    print("Network connection error")
except requests.Timeout:
    print("Request timed out")
except requests.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
except requests.RequestException as e:
    print(f"Request error: {e}")
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/verdic/verdic-guard-python/issues
- Documentation: https://verdic.dev/docs
- Email: support@verdic.dev
