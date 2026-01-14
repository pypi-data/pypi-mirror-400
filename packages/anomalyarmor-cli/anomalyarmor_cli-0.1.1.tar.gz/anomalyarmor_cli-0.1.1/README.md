# AnomalyArmor Python SDK

Python SDK and CLI for AnomalyArmor data observability platform.

## Installation

```bash
pip install anomalyarmor-cli
```

## Quick Start

```python
from anomalyarmor import AnomalyArmorClient

client = AnomalyArmorClient(
    api_key="your-api-key",
    base_url="https://api.anomalyarmor.com"
)

# List assets
assets = client.assets.list()
```

## CLI Usage

```bash
# Configure credentials
armor config set --api-key YOUR_API_KEY --base-url https://api.anomalyarmor.com

# List assets
armor assets list

# Apply configuration from YAML
armor apply config.yaml
```

## Documentation

See [docs.anomalyarmor.com](https://docs.anomalyarmor.com) for full documentation.
