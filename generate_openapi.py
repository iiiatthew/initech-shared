#!/usr/bin/env python3
"""
Generate OpenAPI specification for the FastAPI application.
"""
import json
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

# Get the OpenAPI schema
openapi_schema = app.openapi()

# Save to file
output_file = Path("openapi.json")
with open(output_file, "w") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"OpenAPI specification saved to: {output_file}")
print(f"API Title: {openapi_schema.get('info', {}).get('title')}")
print(f"API Version: {openapi_schema.get('info', {}).get('version')}")
print(f"Total Endpoints: {len(openapi_schema.get('paths', {}))}")

# Also save a YAML version if PyYAML is available
try:
    import yaml
    yaml_file = Path("openapi.yaml")
    with open(yaml_file, "w") as f:
        yaml.dump(openapi_schema, f, default_flow_style=False)
    print(f"YAML version saved to: {yaml_file}")
except ImportError:
    print("PyYAML not available, skipping YAML output")