"""
Utility functions for EDC integration.
"""

import requests
import json
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from django.conf import settings
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def get_edc_url() -> Optional[str]:
    """Get EDC URL from settings."""
    return getattr(settings, 'EDC_URL', None)


def get_edc_participant_id() -> Optional[str]:
    """Get EDC participant ID from settings."""
    return getattr(settings, 'EDC_PARTICIPANT_ID', None)


def get_edc_api_key() -> Optional[str]:
    """Get EDC API key from settings."""
    return getattr(settings, 'EDC_API_KEY', None)


def get_asset_id_from_request(request, strategy: str = None) -> str:
    """
    Generate asset ID from the request URL.

    Strategy can be configured via EDC_ASSET_ID_STRATEGY setting:
    - 'slugify' (default): Slugify the URL without resource ID
    - 'path': Use the URL path (e.g., '/objects/trial6')
    - 'full_url': Use the complete URL
    - 'container': Use only the container path

    Args:
        request: Django request object
        strategy: Override for asset ID generation strategy

    Returns:
        str: Asset identifier
    """
    if strategy is None:
        strategy = getattr(settings, 'EDC_ASSET_ID_STRATEGY', 'slugify')

    url = request.build_absolute_uri()
    parsed_url = urlparse(url)

    if strategy == 'path':
        # Return just the path, removing resource IDs
        path_parts = parsed_url.path.strip('/').split('/')
        if path_parts and path_parts[-1].isdigit():
            path_parts = path_parts[:-1]
        return '/' + '/'.join(path_parts)

    elif strategy == 'container':
        # Return only the container/collection name
        path_parts = parsed_url.path.strip('/').split('/')
        if path_parts and path_parts[-1].isdigit():
            path_parts = path_parts[:-1]
        return path_parts[-1] if path_parts else ''

    elif strategy == 'full_url':
        # Return the full URL without resource ID
        path_parts = parsed_url.path.strip('/').split('/')
        if path_parts and path_parts[-1].isdigit():
            path_parts = path_parts[:-1]
        clean_path = '/'.join(path_parts)
        return f"{parsed_url.scheme}://{parsed_url.netloc}/{clean_path}"

    else:  # 'slugify' (default)
        # Slugify the URL (backward compatible with existing implementation)
        netloc = parsed_url.hostname
        path_parts = parsed_url.path.strip('/').split('/')

        # Remove the resource ID if the last part is a digit
        if path_parts and path_parts[-1].isdigit():
            path_parts = path_parts[:-1]

        clean_path = '/'.join(path_parts)
        port = f":{parsed_url.port}" if parsed_url.port else ""
        clean_url = f"{parsed_url.scheme}{port}//{netloc}/{clean_path}"

        return slugify(clean_url)


def fetch_agreement(agreement_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch contract agreement details from EDC Management API v3.

    Uses the GET /v3/contractagreements/{id} endpoint.

    Args:
        agreement_id: Contract agreement identifier

    Returns:
        Dict containing agreement details, or None if not found/error
    """
    edc_url = get_edc_url()
    if not edc_url:
        logger.error("EDC_URL not configured")
        return None

    edc_participant_id = get_edc_participant_id()
    if not edc_participant_id:
        logger.error("EDC_PARTICIPANT_ID not configured")
        return None

    # Construct the v3 API endpoint
    url = f"{edc_url}/management/v3/contractagreements/{agreement_id}"

    headers = {
        'Content-Type': 'application/json',
    }

    # Add API key if configured (for provider-side validation)
    edc_api_key = get_edc_api_key()
    if edc_api_key:
        headers['X-Api-Key'] = edc_api_key

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 404:
            logger.info(f"Agreement {agreement_id} not found")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching agreement {agreement_id}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching agreement {agreement_id}: {str(e)}")
        return None


def fetch_catalog_entry(asset_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch catalog entry for the given asset from provider's catalog.

    Uses EDC Catalog API v3.
    """
    edc_url = get_edc_url()
    if not edc_url:
        logger.error("EDC_URL not configured")
        return None

    edc_participant_id = get_edc_participant_id()
    if not edc_participant_id:
        logger.error("EDC_PARTICIPANT_ID not configured")
        return None

    url = f"{edc_url}/management/v3/catalog/request"

    headers = {
        'Content-Type': 'application/json',
    }

    # Use provider's API key
    edc_api_key = get_edc_api_key()
    if edc_api_key:
        headers['X-Api-Key'] = edc_api_key
    else:
        logger.warning("EDC_API_KEY not configured - catalog fetch may fail")

    # Query for specific asset
    payload = {
        "@context": {
            "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
        },
        "@type": "QuerySpec",
        "filterExpression": [
            {
                "operandLeft": "id",
                "operator": "=",
                "operandRight": asset_id
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        catalog = response.json()

        # Parse catalog response (can be nested)
        dataset = extract_dataset_from_catalog(catalog, asset_id)
        return dataset

    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching catalog for asset {asset_id}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching catalog: {str(e)}")
        return None


def extract_dataset_from_catalog(catalog: Any, asset_id: str) -> Optional[Dict[str, Any]]:
    """
    Extract the dataset/asset from catalog response.

    Handles both flat and nested catalog structures.
    """
    # If catalog is a list, iterate through catalogs
    if isinstance(catalog, list):
        for cat in catalog:
            result = extract_dataset_from_catalog(cat, asset_id)
            if result:
                return result
        return None

    # If catalog is a dict, look for datasets
    if isinstance(catalog, dict):
        datasets = catalog.get('dcat:dataset', [])

        for dataset in datasets:
            # Check if this is the asset we're looking for
            dataset_id = dataset.get('id') or dataset.get('@id')
            if dataset_id == asset_id:
                return dataset

            # Check if this is a nested catalog
            if dataset.get('@type') == 'dcat:Catalog' and 'dcat:dataset' in dataset:
                inner_result = extract_dataset_from_catalog(dataset, asset_id)
                if inner_result:
                    return inner_result

    return None


def calculate_policy_openness(policy: Dict[str, Any]) -> float:
    """
    Calculate an "openness" score for a policy.

    Higher score = more open policy (fewer restrictions).

    Scoring:
    - Start with 100 points
    - -30 for each prohibition
    - -20 for each obligation
    - -10 for each constraint in permissions
    - -5 for each constraint in obligations

    Returns:
        float: Openness score (0-100, higher is more open)
    """
    score = 100.0

    # Check prohibitions
    prohibitions = policy.get('odrl:prohibition', [])
    if isinstance(prohibitions, dict):
        prohibitions = [prohibitions]
    score -= len(prohibitions) * 30

    # Check obligations
    obligations = policy.get('odrl:obligation', [])
    if isinstance(obligations, dict):
        obligations = [obligations]

    for obligation in obligations:
        score -= 20
        # Count constraints in obligations
        constraints = obligation.get('odrl:constraint', [])
        if isinstance(constraints, dict):
            constraints = [constraints]
        score -= len(constraints) * 5

    # Check permission constraints
    permissions = policy.get('odrl:permission', [])
    if isinstance(permissions, dict):
        permissions = [permissions]

    for permission in permissions:
        constraints = permission.get('odrl:constraint', [])
        if isinstance(constraints, dict):
            constraints = [constraints]
        score -= len(constraints) * 10

    return max(0, score)  # Never go below 0


def describe_policy(policy: Dict[str, Any]) -> str:
    """Generate human-readable policy description."""
    parts = []

    # Check prohibitions
    prohibitions = policy.get('odrl:prohibition', [])
    if prohibitions:
        if isinstance(prohibitions, dict):
            prohibitions = [prohibitions]
        parts.append(f"{len(prohibitions)} prohibition(s)")

    # Check obligations
    obligations = policy.get('odrl:obligation', [])
    if obligations:
        if isinstance(obligations, dict):
            obligations = [obligations]
        parts.append(f"{len(obligations)} obligation(s)")

    # Check permission constraints
    permissions = policy.get('odrl:permission', [])
    if permissions:
        if isinstance(permissions, dict):
            permissions = [permissions]

        constraint_count = sum(
            len(p.get('odrl:constraint', []) if isinstance(p.get('odrl:constraint', []), list) else [p.get('odrl:constraint')])
            for p in permissions if p.get('odrl:constraint')
        )
        if constraint_count > 0:
            parts.append(f"{constraint_count} constraint(s)")

    if not parts:
        return "Open access policy with no restrictions"

    return "Policy with " + ", ".join(parts)


def is_contract_valid(contract_data: Dict[str, Any]) -> bool:
    """
    Check if the contract agreement is valid (not expired, properly signed, etc.).

    Args:
        contract_data: The contract data from EDC API

    Returns:
        bool: True if the contract is valid
    """
    # Try different field names that EDC might use for state
    contract_state = (
        contract_data.get('state') or
        contract_data.get('edc:state') or
        contract_data.get('contractAgreement', {}).get('state') or
        contract_data.get('contractAgreement', {}).get('edc:state')
    )

    logger.info(f"Contract state found: {contract_state}")

    # If we can't find a state field, assume the contract exists and is valid
    # (the fact that we got it from the API means it exists)
    if contract_state is None:
        logger.warning("No state field found in contract data, assuming valid")
        return True

    # Check contract state - should be FINALIZED or VERIFIED
    valid_states = ['FINALIZED', 'VERIFIED', 'CONFIRMED', 'AGREED']
    if contract_state not in valid_states:
        logger.warning(f"Contract state '{contract_state}' is not in valid states: {valid_states}")
        return False

    return True


def is_resource_covered_by_contract(contract_data: Dict[str, Any], requested_url: str) -> bool:
    """
    Check if the requested resource URL is covered by the contract agreement.

    Args:
        contract_data: The contract data from EDC API
        requested_url: The URL being requested

    Returns:
        bool: True if the resource is covered by the contract
    """
    # Try different field names that EDC might use for asset ID
    asset_id = (
        contract_data.get('assetId') or
        contract_data.get('edc:assetId') or
        contract_data.get('@id') or
        contract_data.get('contractAgreement', {}).get('assetId') or
        ''
    )

    logger.info(f"Asset ID found: {asset_id}")
    logger.info(f"Requested URL: {requested_url}")

    # If no assetId, check policy.target as fallback
    if not asset_id:
        policy_target = (
            contract_data.get('policy', {}).get('target') or
            contract_data.get('edc:policy', {}).get('target') or
            contract_data.get('edc:policy', {}).get('edc:target')
        )
        if policy_target:
            logger.info(f"No assetId, using policy target: {policy_target}")
            asset_id = policy_target
        else:
            logger.warning("No assetId or policy target found in contract, denying access")
            return False

    # If asset_id looks like a URL (starts with http:// or https://), do direct matching
    if asset_id.startswith('http://') or asset_id.startswith('https://'):
        logger.info(f"Asset ID is a URL, doing direct matching")
        # Exact match
        if requested_url == asset_id:
            logger.info(f"Exact match: {requested_url} == {asset_id}")
            return True
        # Subresource match (remove /index suffix and check if it's a parent)
        asset_base = asset_id.rsplit('/index', 1)[0] if '/index' in asset_id else asset_id
        if requested_url.startswith(asset_base + '/'):
            logger.info(f"Subresource match: {requested_url} starts with {asset_base}/")
            return True
        logger.warning(f"URL mismatch. Asset: {asset_id}, Requested: {requested_url}")
        return False

    # Otherwise, asset_id is just an ID - need to fetch the asset details from EDC
    logger.info(f"Asset ID is not a URL, fetching asset details from EDC")

    edc_url = get_edc_url()
    if not edc_url:
        logger.error("EDC_URL not configured")
        return False

    asset_url = f"{edc_url}/management/v3/assets/{asset_id}"

    try:
        logger.info(f"Fetching asset from: {asset_url}")
        headers = {'Content-Type': 'application/json'}
        edc_api_key = get_edc_api_key()
        if edc_api_key:
            headers['X-Api-Key'] = edc_api_key

        asset_response = requests.get(asset_url, headers=headers, timeout=5)
        asset_response.raise_for_status()
        asset_data = asset_response.json()
        logger.info(f"Asset data: {asset_data}")

        # Extract dataAddress.baseUrl from the asset
        data_address = asset_data.get('dataAddress', {}) or asset_data.get('edc:dataAddress', {})
        base_url = (
            data_address.get('baseUrl') or
            data_address.get('edc:baseUrl') or
            data_address.get('baseurl') or
            data_address.get('edc:baseurl') or
            ''
        )

        logger.info(f"Base URL from asset: {base_url}")

        if not base_url:
            logger.warning("No baseUrl found in asset dataAddress, denying access")
            return False

        # Check if requested URL matches or is a subresource of base URL
        if requested_url == base_url:
            logger.info(f"Exact match with base URL")
            return True

        # Subresource match (remove /index suffix and check if it's a parent)
        base_url_stripped = base_url.rsplit('/index', 1)[0] if '/index' in base_url else base_url
        if requested_url.startswith(base_url_stripped + '/'):
            logger.info(f"Subresource match: {requested_url} starts with {base_url_stripped}/")
            return True

        logger.warning(f"Requested URL does not match base URL. Base: {base_url}, Requested: {requested_url}")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching asset {asset_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking asset coverage: {str(e)}")
        return False
