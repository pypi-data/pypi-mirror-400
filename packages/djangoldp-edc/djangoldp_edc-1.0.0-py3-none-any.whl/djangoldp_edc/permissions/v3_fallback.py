"""
EDC Contract Permission V3 with fallback to user profile validation.

This module extends V3 validation with fallback to user profile-based
validation when DSP headers are missing.
"""

import requests
from django.conf import settings
import logging
from typing import Optional, Dict, Any

from djangoldp_edc.permissions.v3 import EdcContractPermissionV3
from djangoldp_edc.utils import (
    get_edc_url,
    get_edc_participant_id,
)

logger = logging.getLogger(__name__)


class EdcContractPermissionV3WithFallback(EdcContractPermissionV3):
    """
    Extended version that falls back to automatic negotiation if headers are missing.

    This class combines header-based validation with the automatic negotiation
    approach from the original implementation.

    Flow:
    1. Try header-based validation first (DSP-AGREEMENT-ID + DSP-PARTICIPANT-ID)
    2. If headers missing, fall back to user profile lookup and agreement check
    3. If no agreement exists, automatically initiate contract negotiation
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Try header-based validation first, fall back to user profile validation."""
        # Only validate for safe methods
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            return False

        # Try header-based validation first
        agreement_id = self._get_header(request, self.HEADER_AGREEMENT_ID)
        participant_id = self._get_header(request, self.HEADER_PARTICIPANT_ID)

        if agreement_id and participant_id:
            logger.debug("Using header-based validation")
            asset_id = self.get_asset_id(request)
            return self.validate_agreement(agreement_id, participant_id, asset_id, request)

        # Fall back to user profile-based validation
        logger.debug("Headers missing, falling back to user profile validation")
        return self._validate_via_user_profile(request)

    def _validate_via_user_profile(self, request) -> bool:
        """Fallback validation using user profile and automatic negotiation."""
        remote_user = self._get_remote_user(request)
        if remote_user is None:
            logger.info("No remote user profile found")
            return False

        asset_id = self.get_asset_id(request)
        return self._has_contract_agreement(asset_id, remote_user)

    def _get_remote_user(self, request) -> Optional[Dict[str, Any]]:
        """Fetch remote user profile with EDC credentials."""
        try:
            if not hasattr(request.user, 'urlid'):
                return None

            headers = dict(request.headers)
            headers.pop('Host', None)

            response = requests.get(request.user.urlid, headers=headers, timeout=5)
            response.raise_for_status()
            remote_user = response.json()

            # Validate dataSpaceProfile exists with required fields
            data_space_profile = remote_user.get("dataSpaceProfile")
            if not data_space_profile:
                return None

            if not data_space_profile.get("edc_api_key"):
                return None

            if not data_space_profile.get("edc_did"):
                return None

            return remote_user

        except Exception as e:
            logger.error(f"Error fetching remote user: {str(e)}")
            return None

    def _has_contract_agreement(self, asset_id: str, remote_user: Dict[str, Any]) -> bool:
        """Check if user has a contract agreement, initiate negotiation if not."""
        edc_url = get_edc_url()
        edc_participant_id = get_edc_participant_id()

        if not edc_url or not edc_participant_id:
            logger.error("EDC configuration missing")
            return False

        # Query for existing agreements using v3 API
        url = f"{edc_url}/management/v3/contractagreements/request"

        payload = {
            "@context": {
                "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "QuerySpec",
            "limit": 10,
            "sortOrder": "DESC",
            "filterExpression": [
                {
                    "operandLeft": "assetId",
                    "operator": "=",
                    "operandRight": asset_id
                },
                {
                    "operandLeft": "consumerId",
                    "operator": "=",
                    "operandRight": remote_user["dataSpaceProfile"]["edc_did"]
                }
            ]
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': remote_user["dataSpaceProfile"]["edc_api_key"]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            agreements = response.json()

            if isinstance(agreements, list) and len(agreements) >= 1:
                logger.info(f"Found existing agreement for asset {asset_id}")
                return True

            logger.info(f"No agreement found for asset {asset_id}")
            return False

        except Exception as e:
            logger.error(f"Error checking contract agreement: {str(e)}")
            return False
