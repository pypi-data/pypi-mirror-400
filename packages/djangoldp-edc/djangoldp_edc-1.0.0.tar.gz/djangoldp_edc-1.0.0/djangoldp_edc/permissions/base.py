"""
Original EDC Contract Permission with automatic negotiation.

This module provides the original implementation that uses user profile-based
validation and automatic contract negotiation.
"""

from djangoldp.permissions import LDPBasePermission
import requests
from django.conf import settings
import json
import logging

from djangoldp_edc.utils import (
    get_edc_url,
    get_edc_participant_id,
    get_asset_id_from_request,
)

logger = logging.getLogger(__name__)


class EdcContractPermission(LDPBasePermission):
    """
    Original EDC permission class with automatic contract negotiation.

    This class implements the original approach where:
    1. User credentials are fetched from their remote profile (dataSpaceProfile)
    2. Existing contract agreements are checked
    3. If no agreement exists, automatic negotiation is triggered

    Note: This approach requires the user to have a dataSpaceProfile with:
    - edc_api_key: API key for EDC authentication
    - edc_did: Decentralized Identifier (DID) for the user
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request is for a safe method (GET, HEAD)
        if request.method in ('GET', 'HEAD'):
            remote_user = self.get_remote_user(request)

            if remote_user is None:
                return False

            return self.has_contract_agreement(self.get_asset_id(request), remote_user)

        # For unsafe methods (POST, PUT, PATCH, DELETE), fall back to default behaviour
        return False

    def get_remote_user(self, request):
        """Get the remote user from the request."""
        try:
            headers = dict(request.headers)
            headers.pop('Host', None)

            if hasattr(request.user, 'urlid') is False:
                return None

            remote_user = requests.get(request.user.urlid, headers=headers).json()

            if (remote_user["dataSpaceProfile"] is None):
                return None

            edc_api_key = remote_user["dataSpaceProfile"]["edc_api_key"]
            if edc_api_key is None:
                return None

            user_did = remote_user["dataSpaceProfile"]["edc_did"]
            if user_did is None:
                return None

            return remote_user
        except Exception as e:
            return None

    def get_policy_id_for_asset(self, asset_id, remote_user):
        """
        Retrieve the policy ID for a given asset from the cached catalog.
        Handles nested dcat:dataset structure due to how the MVD has structured its catalogs.
        """
        edc_url = get_edc_url()
        if not edc_url:
            return None

        url = f"{edc_url}/management/v3/catalog/request"
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': remote_user["dataSpaceProfile"]["edc_api_key"]
        }
        payload = json.dumps({
            "@context": {
                "edc": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "CatalogRequest",
            "counterPartyAddress": edc_url,
            "protocol": "dataspace-protocol-http"
        })

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            catalogs = response.json()
            for catalog in catalogs:
                datasets = catalog.get("dcat:dataset", [])
                for dataset in datasets:
                    # If this is a nested catalog, go deeper
                    if dataset.get("@type") == "dcat:Catalog" and "dcat:dataset" in dataset:
                        inner_datasets = dataset.get("dcat:dataset", [])
                        for inner in inner_datasets:
                            if inner.get("id") == asset_id or inner.get("@id") == asset_id:
                                policy = inner.get("odrl:hasPolicy")
                                if policy and "@id" in policy:
                                    return policy["@id"]
                    else:
                        # Top-level dataset
                        if dataset.get("id") == asset_id or dataset.get("@id") == asset_id:
                            policy = dataset.get("odrl:hasPolicy")
                            if policy and "@id" in policy:
                                return policy["@id"]
            return None
        except Exception as e:
            return None

    def negotiate_contract(self, asset_id, policy_id, remote_user):
        """
        Initiate a contract negotiation for the given asset and policy.
        Returns the negotiation ID (receipt) if successful, else None.
        """
        edc_url = get_edc_url()
        if not edc_url:
            return None

        url = f"{edc_url}/consumer/cp/api/management/v3/contractnegotiations"

        edc_participant_id = get_edc_participant_id()
        counterPartyAddress = f"http://{edc_participant_id}-controlplane:8082/api/dsp"

        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': remote_user["dataSpaceProfile"]["edc_api_key"]
        }
        payload = {
            "@context": {
                "edc": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "ContractRequest",
            "counterPartyAddress": counterPartyAddress,
            "counterPartyId": "did:web:provider-identityhub%3A7083:provider",
            "protocol": "dataspace-protocol-http",
            "policy": {
                "@type": "Offer",
                "@id": policy_id,
                "assigner": "did:web:provider-identityhub%3A7083:provider",
                "permission": [],
                "prohibition": [],
                "obligation": {
                    "action": "use",
                    "constraint": {
                        "leftOperand": "DataAccess.level",
                        "operator": "eq",
                        "rightOperand": "processing"
                    }
                },
                "target": asset_id
            },
            "callbackAddresses": []
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            receipt = response.json()
            return receipt.get("@id")  # Return the negotiation ID
        except Exception:
            return None

    def automatic_contract_negotiation(self, asset_id, remote_user):
        """
        Orchestrates the process of negotiating a contract for the given asset.
        Returns True if negotiation was initiated successfully, else False.
        """
        policy_id = self.get_policy_id_for_asset(asset_id, remote_user)
        if not policy_id:
            return False
        negotiation_id = self.negotiate_contract(asset_id, policy_id, remote_user)
        return negotiation_id is not None

    def has_contract_agreement(self, asset_id, remote_user):
        """Check if the user has a contract agreement with the asset."""
        edc_url = get_edc_url()
        edc_participant_id = get_edc_participant_id()

        if not edc_url or not edc_participant_id:
            return False

        url = f"{edc_url}/{edc_participant_id}/cp/api/management/v3/contractagreements/request"
        payload = json.dumps(
            {
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
        )
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': remote_user["dataSpaceProfile"]["edc_api_key"]
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            response_json = response.json()

            # Check if response_json is a list/array and has at least one item
            if isinstance(response_json, list) and len(response_json) >= 1:
                return True
            else:
                # Automatically negotiate for a contract
                # Note: automatic contract negotiation is asynchronous and may not complete immediately.
                self.automatic_contract_negotiation(asset_id, remote_user)
                return False

        except Exception as e:
            return False

    def get_asset_id(self, request):
        """Get the asset ID from the request."""
        return get_asset_id_from_request(request, strategy='slugify')
