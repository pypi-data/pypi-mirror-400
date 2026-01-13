# DjangoLDP EDC

DjangoLDP package for Eclipse Dataspace Connector (EDC) integration and permissions.

## Overview

This package provides permission classes for integrating DjangoLDP applications with the Eclipse Dataspace Connector (EDC). It enables access control based on contract agreements negotiated through the Dataspace Protocol (DSP).

The package supports multiple permission strategies:
- **Header-based validation**: Using DSP headers (`DSP-AGREEMENT-ID`, `DSP-PARTICIPANT-ID`)
- **User profile-based validation**: Using the user's `dataSpaceProfile` with EDC credentials
- **Automatic contract negotiation**: Initiating contract negotiation when no agreement exists
- **Policy discovery**: Returning policy hints for consumer-initiated negotiation

## Installation

```bash
pip install djangoldp-edc
```

## Configuration

### Django Settings

Add to your Django settings:

```python
INSTALLED_APPS = [
    # ...
    'djangoldp',
    'djangoldp_edc',
]

# Add middleware for policy discovery (optional)
MIDDLEWARE = [
    # ...
    'djangoldp_edc.middleware.EdcNegotiationMiddleware',
]

# EDC Configuration (required)
EDC_URL = 'http://your-edc-connector:8082'
EDC_PARTICIPANT_ID = 'your-participant-id'

# Optional settings
EDC_API_KEY = 'your-api-key'  # For provider-side validation
EDC_PROVIDER_DID = 'did:web:your-provider:identifier'  # For auto-negotiation
EDC_AGREEMENT_VALIDATION_ENABLED = True  # Default: True
EDC_AUTO_NEGOTIATION_ENABLED = True  # Default: True
EDC_POLICY_DISCOVERY_ENABLED = True  # Default: True
EDC_ASSET_ID_STRATEGY = 'slugify'  # Options: 'slugify', 'path', 'full_url', 'container'
EDC_POLICY_OPENNESS_THRESHOLD = 0  # Minimum openness score for policies (0-100)
```

### Asset ID Strategies

The `EDC_ASSET_ID_STRATEGY` setting controls how asset IDs are generated from request URLs:

| Strategy | Example URL | Generated Asset ID |
|----------|------------|-------------------|
| `slugify` (default) | `http://localhost:8000/objects/trial6/` | `http8000localhost-objects-trial6` |
| `path` | `http://localhost:8000/objects/trial6/` | `/objects/trial6` |
| `full_url` | `http://localhost:8000/objects/trial6/` | `http://localhost:8000/objects/trial6` |
| `container` | `http://localhost:8000/objects/trial6/` | `trial6` |

## Permission Classes

### EdcContractPermission

**Original implementation with automatic contract negotiation based on user profile.**

This class requires users to have a `dataSpaceProfile` with EDC credentials. It:
1. Fetches the user's remote profile to get EDC credentials
2. Checks for existing contract agreements
3. Automatically initiates contract negotiation if no agreement exists

```python
from djangoldp_edc import EdcContractPermission

class MyModel(Model):
    class Meta(Model.Meta):
        permission_classes = [EdcContractPermission]
```

**Required user profile fields:**
- `dataSpaceProfile.edc_api_key`: API key for EDC authentication
- `dataSpaceProfile.edc_did`: User's Decentralized Identifier (DID)

**Flow:**
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  HTTP Request   │────▶│  Fetch User      │────▶│  Check EDC      │
│  (GET/HEAD)     │     │  Profile         │     │  Credentials    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                        ┌──────────────────┐              ▼
                        │  Auto-Negotiate  │◀────  No Agreement?
                        │  Contract        │              │
                        └──────────────────┘              ▼
                                                   ┌─────────────────┐
                                                   │  Grant/Deny     │
                                                   │  Access         │
                                                   └─────────────────┘
```

---

### EdcContractPermissionV3

**Header-based validation using EDC Management API v3.**

This is the recommended approach for connector-to-connector communication. It validates access based on DSP headers without requiring user profile lookup.

```python
from djangoldp_edc import EdcContractPermissionV3

class MyModel(Model):
    class Meta(Model.Meta):
        permission_classes = [EdcContractPermissionV3]
```

**Required headers:**
- `DSP-AGREEMENT-ID`: Contract agreement identifier
- `DSP-PARTICIPANT-ID`: Consumer's Decentralized Identifier (DID)

**Validation flow:**
1. Extract DSP headers from request
2. Fetch agreement from EDC: `GET /management/v3/contractagreements/{agreementId}`
3. Validate participant ID matches agreement's `consumerId`
4. Validate requested resource is covered by agreement's `assetId`
5. Grant or deny access

**Example request:**
```bash
curl -H "DSP-AGREEMENT-ID: agreement-123" \
     -H "DSP-PARTICIPANT-ID: did:web:consumer:123" \
     http://localhost:8000/objects/trial6/
```

---

### EdcContractPermissionV3WithFallback

**Combines header-based validation with user profile fallback.**

Use this when you need to support both:
- Authenticated connector requests (with DSP headers)
- User browser requests (using user profile credentials)

```python
from djangoldp_edc import EdcContractPermissionV3WithFallback

class MyModel(Model):
    class Meta(Model.Meta):
        permission_classes = [EdcContractPermissionV3WithFallback]
```

**Flow:**
1. Try header-based validation first (DSP-AGREEMENT-ID + DSP-PARTICIPANT-ID)
2. If headers missing, fall back to user profile lookup
3. Check for existing agreements using user's EDC credentials
4. Grant or deny access

---

### EdcContractPermissionV3WithAutoNegotiation

**Automatic contract negotiation when no agreement exists.**

This class extends V3 validation with automatic negotiation capabilities. When no valid agreement exists, it:
1. Fetches the provider's catalog
2. Analyzes available policies using "openness" scoring
3. Selects the most open policy (fewest constraints)
4. Initiates contract negotiation automatically

```python
from djangoldp_edc import EdcContractPermissionV3WithAutoNegotiation

class MyModel(Model):
    class Meta(Model.Meta):
        permission_classes = [EdcContractPermissionV3WithAutoNegotiation]
```

**Additional required header:**
- `DSP-CONSUMER-CONNECTORURL`: Consumer's DSP protocol endpoint

**Important:** Contract negotiation is asynchronous. Access is denied initially, but the client should retry after negotiation completes.

**Policy openness scoring:**
- Start with 100 points
- -30 for each prohibition
- -20 for each obligation
- -10 for each constraint in permissions
- -5 for each constraint in obligations

**Example request:**
```bash
curl -H "DSP-PARTICIPANT-ID: did:web:consumer:123" \
     -H "DSP-CONSUMER-CONNECTORURL: http://consumer:8082/api/dsp" \
     http://localhost:8000/objects/trial6/
```

---

### EdcContractPermissionV3PolicyDiscovery

**Policy discovery with consumer-initiated negotiation (correct DSP architecture).**

This class implements the correct Dataspace Protocol architecture where the **consumer** initiates contract negotiation, not the provider. When no agreement exists, it returns a 449 (Retry With) response containing policy hints.

```python
from djangoldp_edc import EdcContractPermissionV3PolicyDiscovery

class MyModel(Model):
    class Meta(Model.Meta):
        permission_classes = [EdcContractPermissionV3PolicyDiscovery]
```

**Response when negotiation required (HTTP 449):**
```json
{
    "error": "contract_agreement_required",
    "asset_id": "/objects/trial6",
    "participant_id": "did:web:consumer:123",
    "catalog_url": "https://provider-edc:8082/api/catalog",
    "suggested_policies": [
        {
            "policy_id": "policy-open-123",
            "openness_score": 100,
            "description": "Open access policy with no restrictions"
        }
    ],
    "instructions": "Initiate contract negotiation via your EDC connector"
}
```

**Response headers:**
- `X-EDC-Catalog-URL`: Provider's catalog URL
- `X-EDC-Asset-ID`: Asset identifier
- `X-EDC-Suggested-Policy`: Best policy ID
- `X-EDC-Policy-Openness`: Policy openness score
- `Retry-After`: Suggested retry interval

**Requires middleware:**
```python
MIDDLEWARE = [
    # ...
    'djangoldp_edc.middleware.EdcNegotiationMiddleware',
]
```

---

## DSP Headers Reference

| Header | Description | Required By |
|--------|-------------|-------------|
| `DSP-AGREEMENT-ID` | Contract agreement identifier | V3, V3WithFallback, V3WithAutoNegotiation, V3PolicyDiscovery |
| `DSP-PARTICIPANT-ID` | Consumer's DID | All V3 classes |
| `DSP-CONSUMER-CONNECTORURL` | Consumer's DSP endpoint | V3WithAutoNegotiation |

## Usage with djangoldp-indexing

Configure permission classes for indexing views:

```python
DJANGOLDP_INDEXING_PERMISSION_CLASSES = [
    'djangoldp_edc.permissions.EdcContractPermissionV3',
]
```

## Security Architecture

### API Key Separation

Each party uses only their own API key:
- Consumer's API key → Consumer's EDC connector only
- Provider's API key → Provider's EDC connector only

**No API keys are ever shared between parties.**

Only public identifiers are transmitted:
- DIDs (Decentralized Identifiers)
- Agreement IDs
- Asset IDs
- Connector URLs

### Contract Agreement Validation

The permission classes validate:
1. Agreement exists in EDC
2. Agreement state is valid (FINALIZED, VERIFIED, CONFIRMED, or AGREED)
3. Consumer ID matches the requesting participant
4. Asset ID covers the requested resource (including subresources)

## API Reference

### Utility Functions

```python
from djangoldp_edc.utils import (
    get_edc_url,                    # Get EDC URL from settings
    get_edc_participant_id,         # Get participant ID from settings
    get_edc_api_key,                # Get API key from settings
    get_asset_id_from_request,      # Generate asset ID from request
    fetch_agreement,                # Fetch agreement from EDC
    fetch_catalog_entry,            # Fetch catalog entry for asset
    calculate_policy_openness,      # Calculate policy openness score
    describe_policy,                # Generate policy description
    is_contract_valid,              # Check if contract is valid
    is_resource_covered_by_contract,# Check if resource is covered
)
```

### Exceptions

```python
from djangoldp_edc import NegotiationRequired

# Raised when contract negotiation is required
# Caught by EdcNegotiationMiddleware and converted to 449 response
raise NegotiationRequired(
    asset_id='/objects/trial6',
    participant_id='did:web:consumer:123',
    suggested_policies=[...]
)
```

## Testing

Run the test suite:

```bash
python -m unittest djangoldp_edc.tests.runner
```

Run specific test modules:

```bash
python -m unittest djangoldp_edc.tests.test_permissions
python -m unittest djangoldp_edc.tests.test_permissions_v3
python -m unittest djangoldp_edc.tests.test_utils
python -m unittest djangoldp_edc.tests.test_middleware
```

## Migration from djangoldp-tems

If you were using permission classes from `djangoldp-tems`, update your imports:

```python
# Old (deprecated)
from djangoldp_tems.permissions import EdcContractPermission
from djangoldp_tems.permissions_v3 import EdcContractPermissionV3

# New (recommended)
from djangoldp_edc import EdcContractPermission
from djangoldp_edc import EdcContractPermissionV3
```

The old imports still work but will emit deprecation warnings.

## License

MIT License

## Contributing

Contributions are welcome! Please submit issues and pull requests to:
https://git.startinblox.com/djangoldp-packages/djangoldp-edc
