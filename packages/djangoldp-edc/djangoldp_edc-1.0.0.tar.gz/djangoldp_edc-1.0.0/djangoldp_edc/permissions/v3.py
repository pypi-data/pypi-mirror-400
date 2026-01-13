"""
EDC Contract Permission V3 with header-based validation.

This module provides the base V3 implementation that validates access
based on DSP headers (DSP-AGREEMENT-ID, DSP-PARTICIPANT-ID).
"""

from djangoldp.permissions import LDPBasePermission
from django.conf import settings
import logging
from typing import Optional, Dict, Any

from djangoldp_edc.utils import (
    get_asset_id_from_request,
    fetch_agreement,
    is_resource_covered_by_contract,
)

logger = logging.getLogger(__name__)


class EdcContractPermissionV3(LDPBasePermission):
    """
    EDC-based permission class using Management API v3 with header-based validation.

    This permission class validates access to resources based on DSP headers:
    - DSP-AGREEMENT-ID: The contract agreement identifier
    - DSP-PARTICIPANT-ID: The participant's decentralized identifier (DID)

    The class verifies that:
    1. Both headers are present in the request
    2. The agreement exists and is valid in the EDC connector
    3. The agreement's assetId matches the requested resource
    4. The participant ID matches the agreement's consumer

    Configuration:
    - EDC_URL: Base URL of the EDC connector (required)
    - EDC_PARTICIPANT_ID: This participant's identifier (required)
    - EDC_API_KEY: API key for EDC Management API (optional, for provider-side validation)
    - EDC_AGREEMENT_VALIDATION_ENABLED: Enable/disable validation (default: True)
    - EDC_ASSET_ID_STRATEGY: Strategy for asset ID generation ('slugify', 'path', 'full_url')
    """

    # Header names following DSP conventions
    HEADER_AGREEMENT_ID = 'DSP-AGREEMENT-ID'
    HEADER_PARTICIPANT_ID = 'DSP-PARTICIPANT-ID'
    HEADER_CONSUMER_CONNECTOR_URL = 'DSP-CONSUMER-CONNECTORURL'

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Validate object-level permissions based on EDC contract agreement.
        """
        # Only validate for safe methods (GET, HEAD, OPTIONS)
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

        if not agreement_id or not participant_id:
            logger.info(
                f"Missing DSP headers - agreement_id: {bool(agreement_id)}, "
                f"participant_id: {bool(participant_id)}"
            )
            return False

        # Get asset ID for the requested resource
        asset_id = self.get_asset_id(request)

        # Validate the agreement
        return self.validate_agreement(
            agreement_id=agreement_id,
            participant_id=participant_id,
            asset_id=asset_id,
            request=request
        )

    def has_permission(self, request, view) -> bool:
        """
        Validate container/index-level permissions based on EDC contract agreement.
        """
        # Only validate for safe methods
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            return False

        # Check if validation is enabled
        if not getattr(settings, 'EDC_AGREEMENT_VALIDATION_ENABLED', True):
            return True

        # Extract DSP headers
        agreement_id = self._get_header(request, self.HEADER_AGREEMENT_ID)
        participant_id = self._get_header(request, self.HEADER_PARTICIPANT_ID)

        if not agreement_id or not participant_id:
            logger.info("Missing DSP headers for container access")
            return False

        # Get asset ID for the requested index/container
        asset_id = self.get_asset_id(request)

        # Validate the agreement
        return self.validate_agreement(
            agreement_id=agreement_id,
            participant_id=participant_id,
            asset_id=asset_id,
            request=request
        )

    def validate_agreement(
        self,
        agreement_id: str,
        participant_id: str,
        asset_id: str,
        request
    ) -> bool:
        """
        Validate that the agreement is valid for the given participant and asset.
        """
        try:
            # Fetch the agreement from EDC Management API v3
            agreement = fetch_agreement(agreement_id)

            if not agreement:
                logger.warning(f"Agreement {agreement_id} not found")
                return False

            # Validate participant ID matches consumer
            if not self._validate_participant(agreement, participant_id):
                logger.warning(
                    f"Participant ID mismatch - header: {participant_id}, "
                    f"agreement consumer: {agreement.get('consumerId')}"
                )
                return False

            # Validate asset ID matches the agreement
            if not self._validate_asset(agreement, asset_id, request):
                logger.warning(
                    f"Asset ID mismatch - requested: {asset_id}, "
                    f"agreement asset: {agreement.get('assetId')}"
                )
                return False

            logger.info(
                f"Access granted - agreement: {agreement_id}, "
                f"participant: {participant_id}, asset: {asset_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error validating agreement: {str(e)}", exc_info=True)
            return False

    def _validate_participant(self, agreement: Dict[str, Any], participant_id: str) -> bool:
        """Validate that the participant ID matches the agreement's consumer."""
        consumer_id = agreement.get('consumerId')
        if not consumer_id:
            logger.warning("Agreement missing consumerId")
            return False

        # Direct match
        if consumer_id == participant_id:
            return True

        # Handle potential formatting differences (e.g., URL encoding)
        normalized_consumer = consumer_id.strip().lower()
        normalized_participant = participant_id.strip().lower()

        return normalized_consumer == normalized_participant

    def _validate_asset(self, agreement: Dict[str, Any], asset_id: str, request) -> bool:
        """
        Validate that the requested resource URL is covered by the agreement's asset.
        """
        agreement_asset_id = agreement.get('assetId')
        if not agreement_asset_id:
            logger.warning("Agreement missing assetId")
            return False

        # Get the requested URL
        requested_url = request.build_absolute_uri()
        logger.info(f"Validating asset - Agreement assetId: {agreement_asset_id}, Requested URL: {requested_url}")

        # If assetId looks like a URL, do direct matching
        if agreement_asset_id.startswith('http://') or agreement_asset_id.startswith('https://'):
            logger.info(f"Asset ID is a URL, doing direct matching")

            # Exact match
            if requested_url == agreement_asset_id:
                return True

            # Subresource match
            asset_base = agreement_asset_id.rstrip('/')
            if '/index' in asset_base:
                asset_base = asset_base.rsplit('/index', 1)[0]

            requested_base = requested_url.rstrip('/')
            url_parts = requested_base.split('/')
            if url_parts and url_parts[-1].isdigit():
                requested_base = '/'.join(url_parts[:-1])

            if requested_base.startswith(asset_base + '/') or requested_base == asset_base:
                return True

            logger.warning(f"URL mismatch. Asset: {agreement_asset_id}, Requested: {requested_url}")
            return False

        # Asset ID is not a URL - fetch asset details from EDC
        return is_resource_covered_by_contract(agreement, requested_url)

    def get_asset_id(self, request) -> str:
        """Generate asset ID from the request URL."""
        return get_asset_id_from_request(request)

    def _get_header(self, request, header_name: str) -> Optional[str]:
        """Extract a header value from the request, handling case-insensitivity."""
        if hasattr(request, 'headers'):
            return request.headers.get(header_name)

        # Fallback for older Django versions
        header_key = f"HTTP_{header_name.upper().replace('-', '_')}"
        return request.META.get(header_key)
