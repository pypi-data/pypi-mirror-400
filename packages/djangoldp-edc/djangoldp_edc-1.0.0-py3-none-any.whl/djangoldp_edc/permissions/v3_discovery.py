"""
EDC Contract Permission V3 with policy discovery.

This module implements the correct DSP architecture where the consumer
initiates contract negotiation. When no agreement exists, it returns
policy hints for consumer-initiated negotiation.
"""

from djangoldp.permissions import LDPBasePermission
from django.conf import settings
import logging
from typing import Optional, Dict, Any, List

from djangoldp_edc.permissions.v3 import EdcContractPermissionV3
from djangoldp_edc.utils import (
    get_asset_id_from_request,
    fetch_catalog_entry,
    calculate_policy_openness,
    describe_policy,
)
from djangoldp_edc.exceptions import NegotiationRequired

logger = logging.getLogger(__name__)


class EdcContractPermissionV3PolicyDiscovery(LDPBasePermission):
    """
    EDC permission with policy discovery - CORRECT architecture.

    When no valid agreement exists:
    1. Analyzes available policies
    2. Returns 449 (Retry With) + policy information
    3. Consumer's connector initiates negotiation
    4. Consumer retries with agreement ID

    This respects the EDC model where CONSUMER initiates negotiations.

    Response format (when negotiation needed):
    HTTP/1.1 449 Retry With
    Content-Type: application/json
    X-EDC-Catalog-URL: https://provider-edc:8082/api/catalog
    X-EDC-Asset-ID: /objects/trial6
    X-EDC-Suggested-Policy: policy-open-123
    """

    HEADER_AGREEMENT_ID = 'DSP-AGREEMENT-ID'
    HEADER_PARTICIPANT_ID = 'DSP-PARTICIPANT-ID'
    HEADER_CONSUMER_CONNECTOR_URL = 'DSP-CONSUMER-CONNECTORURL'

    def has_object_permission(self, request, view, obj) -> bool:
        """Validate with policy discovery fallback."""
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            return False

        agreement_id = self._get_header(request, self.HEADER_AGREEMENT_ID)
        participant_id = self._get_header(request, self.HEADER_PARTICIPANT_ID)

        if not participant_id:
            logger.info("Missing DSP-PARTICIPANT-ID")
            return False

        asset_id = self.get_asset_id(request)

        # If agreement provided, validate it
        if agreement_id:
            validator = EdcContractPermissionV3()
            return validator.validate_agreement(
                agreement_id=agreement_id,
                participant_id=participant_id,
                asset_id=asset_id,
                request=request
            )

        # No agreement - provide policy discovery
        if getattr(settings, 'EDC_POLICY_DISCOVERY_ENABLED', True):
            suggested_policies = self._discover_policies(asset_id, participant_id)

            if suggested_policies:
                # Raise exception that middleware will catch
                raise NegotiationRequired(asset_id, participant_id, suggested_policies)

        # Policy discovery disabled or no policies found
        return False

    def has_permission(self, request, view) -> bool:
        """Container-level validation."""
        return self.has_object_permission(request, view, None)

    def _discover_policies(
        self,
        asset_id: str,
        participant_id: str
    ) -> List[Dict[str, Any]]:
        """Discover and rank policies for the asset."""
        try:
            # Fetch catalog entry
            catalog_entry = fetch_catalog_entry(asset_id)
            if not catalog_entry:
                return []

            # Extract and score policies
            policies = self._extract_and_score_policies(catalog_entry)

            # Filter by threshold
            threshold = getattr(settings, 'EDC_POLICY_OPENNESS_THRESHOLD', 0)
            suitable_policies = [
                p for p in policies if p['openness_score'] >= threshold
            ]

            # Sort by score (highest first)
            suitable_policies.sort(key=lambda p: p['openness_score'], reverse=True)

            return suitable_policies[:5]  # Return top 5

        except Exception as e:
            logger.error(f"Error discovering policies: {str(e)}", exc_info=True)
            return []

    def _extract_and_score_policies(
        self,
        dataset: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract policies and calculate openness scores."""
        policy = dataset.get('odrl:hasPolicy')
        if not policy:
            return []

        policies = [policy] if isinstance(policy, dict) else policy

        scored_policies = []
        for pol in policies:
            policy_id = pol.get('@id') or pol.get('id')
            if not policy_id:
                continue

            score = calculate_policy_openness(pol)
            description = describe_policy(pol)

            scored_policies.append({
                'policy_id': policy_id,
                'openness_score': score,
                'description': description,
                'policy': pol
            })

        return scored_policies

    def get_asset_id(self, request) -> str:
        """Generate asset ID from request."""
        return get_asset_id_from_request(request)

    def _get_header(self, request, header_name: str) -> Optional[str]:
        """Extract header."""
        if hasattr(request, 'headers'):
            return request.headers.get(header_name)
        header_key = f"HTTP_{header_name.upper().replace('-', '_')}"
        return request.META.get(header_key)
