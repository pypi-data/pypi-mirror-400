"""
EDC Middleware for handling contract negotiation exceptions.
"""

from django.http import JsonResponse
from django.conf import settings

from djangoldp_edc.exceptions import NegotiationRequired


class EdcNegotiationMiddleware:
    """
    Middleware to convert NegotiationRequired exceptions to proper HTTP responses.

    Add to MIDDLEWARE in settings.py:
        'djangoldp_edc.middleware.EdcNegotiationMiddleware',

    Response format (when negotiation needed):
    HTTP/1.1 449 Retry With
    Content-Type: application/json
    X-EDC-Catalog-URL: https://provider-edc:8082/api/catalog
    X-EDC-Asset-ID: /objects/trial6
    X-EDC-Suggested-Policy: policy-open-123

    {
        "error": "contract_agreement_required",
        "asset_id": "/objects/trial6",
        "participant_id": "did:web:consumer:123",
        "catalog_url": "https://provider-edc:8082/api/catalog",
        "suggested_policies": [...],
        "instructions": "Initiate contract negotiation via your EDC connector"
    }
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Handle NegotiationRequired exceptions."""
        if isinstance(exception, NegotiationRequired):
            # Get provider's catalog URL
            edc_url = getattr(settings, 'EDC_URL', 'http://localhost')
            edc_participant_id = getattr(settings, 'EDC_PARTICIPANT_ID', 'provider')
            catalog_url = f"{edc_url}/management/v3/catalog/request"

            response_data = {
                'error': 'contract_agreement_required',
                'asset_id': exception.asset_id,
                'participant_id': exception.participant_id,
                'catalog_url': catalog_url,
                'suggested_policies': exception.suggested_policies,
                'instructions': (
                    'No valid contract agreement found. '
                    'Your EDC connector should initiate contract negotiation '
                    'using one of the suggested policies, then retry this request '
                    'with the DSP-AGREEMENT-ID header.'
                )
            }

            response = JsonResponse(response_data, status=449)

            # Add helpful headers
            response['X-EDC-Catalog-URL'] = catalog_url
            response['X-EDC-Asset-ID'] = exception.asset_id

            if exception.suggested_policies:
                # Add the best policy as a header
                response['X-EDC-Suggested-Policy'] = exception.suggested_policies[0]['policy_id']
                response['X-EDC-Policy-Openness'] = str(exception.suggested_policies[0]['openness_score'])

            response['Retry-After'] = '10'  # Suggest retry after 10 seconds

            return response

        return None
