"""
EDC Contract Permissions for DjangoLDP.

This package provides permission classes for integrating with Eclipse Dataspace Connector (EDC)
to control access to resources based on contract agreements.

Permission Classes:
- EdcContractPermission: Original implementation with automatic negotiation
- EdcContractPermissionV3: Header-based validation using EDC Management API v3
- EdcContractPermissionV3WithFallback: V3 with fallback to user profile validation
- EdcContractPermissionV3WithAutoNegotiation: V3 with automatic contract negotiation
- EdcContractPermissionV3PolicyDiscovery: V3 with policy discovery (correct architecture)

Configuration Settings:
- EDC_URL: Base URL of the EDC connector (required)
- EDC_PARTICIPANT_ID: This participant's identifier (required)
- EDC_API_KEY: API key for EDC Management API (optional)
- EDC_ASSET_ID_STRATEGY: Strategy for asset ID generation ('slugify', 'path', 'full_url', 'container')
- EDC_AGREEMENT_VALIDATION_ENABLED: Enable/disable validation (default: True)
- EDC_AUTO_NEGOTIATION_ENABLED: Enable/disable auto-negotiation (default: True)
- EDC_POLICY_OPENNESS_THRESHOLD: Minimum openness score to trigger negotiation (default: 0)
- EDC_POLICY_DISCOVERY_ENABLED: Enable/disable policy discovery (default: True)

DSP Headers:
- DSP-AGREEMENT-ID: Contract agreement identifier
- DSP-PARTICIPANT-ID: Participant's decentralized identifier (DID)
- DSP-CONSUMER-CONNECTORURL: Consumer's DSP protocol endpoint
"""

from djangoldp_edc.permissions.base import EdcContractPermission
from djangoldp_edc.permissions.v3 import EdcContractPermissionV3
from djangoldp_edc.permissions.v3_fallback import EdcContractPermissionV3WithFallback
from djangoldp_edc.permissions.v3_auto import EdcContractPermissionV3WithAutoNegotiation
from djangoldp_edc.permissions.v3_discovery import EdcContractPermissionV3PolicyDiscovery

__all__ = [
    'EdcContractPermission',
    'EdcContractPermissionV3',
    'EdcContractPermissionV3WithFallback',
    'EdcContractPermissionV3WithAutoNegotiation',
    'EdcContractPermissionV3PolicyDiscovery',
]
