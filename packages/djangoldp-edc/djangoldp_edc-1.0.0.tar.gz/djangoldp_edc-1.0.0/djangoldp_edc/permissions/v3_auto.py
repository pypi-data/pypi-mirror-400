"""
EDC Contract Permission V3 with automatic contract negotiation.

This module extends V3 validation with automatic negotiation capabilities
when no agreement exists.
"""

import requests
from django.conf import settings
import logging
from typing import Optional, Dict, Any

from djangoldp_edc.permissions.v3 import EdcContractPermissionV3
from djangoldp_edc.utils import (
    get_edc_url,
    get_edc_participant_id,
    get_edc_api_key,
    fetch_catalog_entry,
    calculate_policy_openness,
)

logger = logging.getLogger(__name__)


class EdcContractPermissionV3WithAutoNegotiation(EdcContractPermissionV3):
    """
    EDC permission class with automatic contract negotiation.

    This class extends the base V3 permission with automatic negotiation capabilities
    when no agreement exists. It looks for "open" policies and initiates negotiation.

    Flow:
    1. Check for DSP-AGREEMENT-ID header
    2. If present and valid, grant access immediately
    3. If missing or agreement not found, check for DSP-CONSUMER-CONNECTORURL
    4. If connector URL present, fetch catalog and analyze policies
    5. Find the most "open" policy (fewest/no constraints)
    6. Initiate contract negotiation automatically
    7. Return False (access denied) but negotiation is in progress

    Headers used:
    - DSP-AGREEMENT-ID: Contract agreement ID (optional if negotiating)
    - DSP-PARTICIPANT-ID: Consumer's participant/DID (required)
    - DSP-CONSUMER-CONNECTORURL: Consumer's DSP endpoint (required for auto-negotiation)

    Note: Provider uses their own EDC_API_KEY to communicate with their EDC connector.
    Consumer's API key is never shared.

    Configuration:
    - EDC_AUTO_NEGOTIATION_ENABLED: Enable/disable auto-negotiation (default: True)
    - EDC_CATALOG_API_VERSION: Catalog API version to use (default: 'v3')
    - EDC_POLICY_OPENNESS_THRESHOLD: Minimum openness score to trigger negotiation (default: 0)
    - EDC_API_KEY: Provider's API key for their EDC connector (required)
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Validate with automatic negotiation fallback."""
        # Only validate for safe methods
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            logger.debug(f"Unsafe method {request.method} - denying access")
            return False

        # Check if validation is enabled
        if not getattr(settings, 'EDC_AGREEMENT_VALIDATION_ENABLED', True):
            logger.warning("EDC agreement validation is disabled - allowing access")
            return True

        # Extract DSP headers
        agreement_id = self._get_header(request, self.HEADER_AGREEMENT_ID)
        participant_id = self._get_header(request, self.HEADER_PARTICIPANT_ID)
        consumer_connector_url = self._get_header(request, self.HEADER_CONSUMER_CONNECTOR_URL)

        # Get asset ID for the requested resource
        asset_id = self.get_asset_id(request)

        # Path 1: Agreement ID provided - validate it
        if agreement_id and participant_id:
            logger.debug("Agreement ID provided - validating")
            is_valid = self.validate_agreement(
                agreement_id=agreement_id,
                participant_id=participant_id,
                asset_id=asset_id,
                request=request
            )
            if is_valid:
                return True

            logger.info(f"Agreement validation failed for {agreement_id}")

        # Path 2: No agreement or agreement invalid - try auto-negotiation
        if not getattr(settings, 'EDC_AUTO_NEGOTIATION_ENABLED', True):
            logger.info("Auto-negotiation disabled - denying access")
            return False

        if not participant_id:
            logger.info("Missing DSP-PARTICIPANT-ID - cannot auto-negotiate")
            return False

        if not consumer_connector_url:
            logger.info("Missing DSP-CONSUMER-CONNECTORURL - cannot auto-negotiate")
            return False

        # Try automatic negotiation
        logger.info(
            f"Attempting automatic negotiation for participant {participant_id}, "
            f"asset {asset_id}"
        )

        negotiation_id = self._auto_negotiate(
            participant_id=participant_id,
            consumer_connector_url=consumer_connector_url,
            asset_id=asset_id,
            request=request
        )

        if negotiation_id:
            logger.info(
                f"Contract negotiation initiated: {negotiation_id}. "
                f"Access currently denied but negotiation in progress."
            )
            return False
        else:
            logger.warning(f"Failed to initiate contract negotiation for asset {asset_id}")
            return False

    def has_permission(self, request, view) -> bool:
        """Container-level validation with auto-negotiation support."""
        return self.has_object_permission(request, view, None)

    def _auto_negotiate(
        self,
        participant_id: str,
        consumer_connector_url: str,
        asset_id: str,
        request
    ) -> Optional[str]:
        """Automatically negotiate a contract for the given asset."""
        try:
            # Step 1: Fetch catalog and find the asset
            catalog_entry = fetch_catalog_entry(asset_id)
            if not catalog_entry:
                logger.warning(f"Asset {asset_id} not found in catalog")
                return None

            # Step 2: Analyze policies and find the most "open" one
            policy = self._find_most_open_policy(catalog_entry)
            if not policy:
                logger.warning(f"No suitable policy found for asset {asset_id}")
                return None

            policy_id = policy.get('@id') or policy.get('id')
            if not policy_id:
                logger.error("Policy missing @id field")
                return None

            logger.info(f"Selected policy {policy_id} for asset {asset_id}")

            # Step 3: Initiate contract negotiation
            negotiation_id = self._initiate_negotiation(
                asset_id=asset_id,
                policy_id=policy_id,
                policy=policy,
                participant_id=participant_id,
                consumer_connector_url=consumer_connector_url,
                request=request
            )

            return negotiation_id

        except Exception as e:
            logger.error(f"Error during auto-negotiation: {str(e)}", exc_info=True)
            return None

    def _find_most_open_policy(self, dataset: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the most "open" policy from the dataset."""
        policy = dataset.get('odrl:hasPolicy')

        if not policy:
            logger.warning("Dataset has no policy")
            return None

        # Handle single policy
        if isinstance(policy, dict):
            policies = [policy]
        elif isinstance(policy, list):
            policies = policy
        else:
            logger.warning(f"Unexpected policy format: {type(policy)}")
            return None

        # Score each policy and select the most open one
        best_policy = None
        best_score = -1

        for pol in policies:
            score = calculate_policy_openness(pol)
            logger.debug(f"Policy {pol.get('@id', 'unknown')} openness score: {score}")

            if score > best_score:
                best_score = score
                best_policy = pol

        # Check if policy meets minimum openness threshold
        threshold = getattr(settings, 'EDC_POLICY_OPENNESS_THRESHOLD', 0)
        if best_score < threshold:
            logger.info(f"Best policy score {best_score} below threshold {threshold}")
            return None

        return best_policy

    def _initiate_negotiation(
        self,
        asset_id: str,
        policy_id: str,
        policy: Dict[str, Any],
        participant_id: str,
        consumer_connector_url: str,
        request
    ) -> Optional[str]:
        """Initiate contract negotiation with the provider."""
        edc_url = get_edc_url()
        if not edc_url:
            logger.error("EDC_URL not configured")
            return None

        edc_participant_id = get_edc_participant_id()
        if not edc_participant_id:
            logger.error("EDC_PARTICIPANT_ID not configured")
            return None

        # Construct negotiation endpoint
        url = f"{edc_url}/management/v3/contractnegotiations"

        headers = {
            'Content-Type': 'application/json',
        }

        # Use provider's API key for negotiation
        edc_api_key = get_edc_api_key()
        if edc_api_key:
            headers['X-Api-Key'] = edc_api_key
        else:
            logger.error("EDC_API_KEY not configured - negotiation will fail")
            return None

        # Get provider DID (this connector's DID)
        provider_did = getattr(settings, 'EDC_PROVIDER_DID', None)
        if not provider_did:
            logger.error("EDC_PROVIDER_DID not configured")
            return None

        # Build negotiation request payload
        payload = {
            "@context": [
                "https://w3id.org/edc/v0.0.1/ns/"
            ],
            "@type": "ContractRequest",
            "counterPartyAddress": consumer_connector_url,
            "counterPartyId": participant_id,
            "protocol": "dataspace-protocol-http",
            "policy": {
                "@type": "Offer",
                "@id": policy_id,
                "assigner": provider_did,
                "target": asset_id,
                "odrl:permission": policy.get('odrl:permission', []),
                "odrl:prohibition": policy.get('odrl:prohibition', []),
                "odrl:obligation": policy.get('odrl:obligation', [])
            },
            "callbackAddresses": []
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            receipt = response.json()

            negotiation_id = receipt.get('@id') or receipt.get('id')
            logger.info(f"Contract negotiation initiated: {negotiation_id}")
            return negotiation_id

        except requests.exceptions.Timeout:
            logger.error("Timeout initiating contract negotiation")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating negotiation: {str(e)}")
            return None
