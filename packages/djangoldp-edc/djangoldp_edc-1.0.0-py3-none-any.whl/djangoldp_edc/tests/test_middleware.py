"""
Tests for EDC middleware.
"""

from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse, JsonResponse
from unittest.mock import Mock, patch
import json

from djangoldp_edc.middleware import EdcNegotiationMiddleware
from djangoldp_edc.exceptions import NegotiationRequired


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
)
class EdcNegotiationMiddlewareTestCase(TestCase):
    """Tests for EdcNegotiationMiddleware."""

    def setUp(self):
        self.factory = RequestFactory()

        def get_response(request):
            return HttpResponse("OK")

        self.middleware = EdcNegotiationMiddleware(get_response)

    def test_passes_through_normal_requests(self):
        """Test that normal requests pass through unchanged."""
        request = self.factory.get('/')

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_handles_negotiation_required_exception(self):
        """Test that NegotiationRequired exception is converted to 449 response."""
        request = self.factory.get('/objects/trial6/')

        suggested_policies = [{
            'policy_id': 'policy-open-123',
            'openness_score': 100,
            'description': 'Open access policy'
        }]

        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=suggested_policies
        )

        response = self.middleware.process_exception(request, exception)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 449)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_449_response_contains_required_fields(self):
        """Test that 449 response contains all required fields."""
        request = self.factory.get('/objects/trial6/')

        suggested_policies = [{
            'policy_id': 'policy-open-123',
            'openness_score': 100,
            'description': 'Open access policy'
        }]

        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=suggested_policies
        )

        response = self.middleware.process_exception(request, exception)
        data = json.loads(response.content)

        self.assertEqual(data['error'], 'contract_agreement_required')
        self.assertEqual(data['asset_id'], '/objects/trial6')
        self.assertEqual(data['participant_id'], 'did:web:consumer:123')
        self.assertIn('catalog_url', data)
        self.assertIn('suggested_policies', data)
        self.assertIn('instructions', data)

    def test_449_response_includes_headers(self):
        """Test that 449 response includes helpful headers."""
        request = self.factory.get('/objects/trial6/')

        suggested_policies = [{
            'policy_id': 'policy-open-123',
            'openness_score': 100,
            'description': 'Open access policy'
        }]

        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=suggested_policies
        )

        response = self.middleware.process_exception(request, exception)

        self.assertIn('X-EDC-Catalog-URL', response)
        self.assertIn('X-EDC-Asset-ID', response)
        self.assertEqual(response['X-EDC-Asset-ID'], '/objects/trial6')
        self.assertIn('X-EDC-Suggested-Policy', response)
        self.assertEqual(response['X-EDC-Suggested-Policy'], 'policy-open-123')
        self.assertIn('X-EDC-Policy-Openness', response)
        self.assertEqual(response['X-EDC-Policy-Openness'], '100')
        self.assertIn('Retry-After', response)

    def test_ignores_other_exceptions(self):
        """Test that other exceptions are not handled."""
        request = self.factory.get('/')

        exception = ValueError("Some other error")

        response = self.middleware.process_exception(request, exception)

        self.assertIsNone(response)

    def test_handles_empty_suggested_policies(self):
        """Test handling when no policies are suggested."""
        request = self.factory.get('/objects/trial6/')

        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=[]
        )

        response = self.middleware.process_exception(request, exception)

        self.assertEqual(response.status_code, 449)
        # Should not have policy headers when no policies
        self.assertNotIn('X-EDC-Suggested-Policy', response)


class NegotiationRequiredExceptionTestCase(TestCase):
    """Tests for NegotiationRequired exception."""

    def test_creates_with_required_fields(self):
        """Test exception creation with required fields."""
        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=[]
        )

        self.assertEqual(exception.asset_id, '/objects/trial6')
        self.assertEqual(exception.participant_id, 'did:web:consumer:123')
        self.assertEqual(exception.suggested_policies, [])
        self.assertEqual(exception.status_code, 449)

    def test_has_meaningful_message(self):
        """Test that exception has meaningful message."""
        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=[]
        )

        self.assertIn('/objects/trial6', str(exception))

    def test_stores_suggested_policies(self):
        """Test that suggested policies are stored correctly."""
        policies = [
            {'policy_id': 'p1', 'openness_score': 100},
            {'policy_id': 'p2', 'openness_score': 80}
        ]

        exception = NegotiationRequired(
            asset_id='/objects/trial6',
            participant_id='did:web:consumer:123',
            suggested_policies=policies
        )

        self.assertEqual(len(exception.suggested_policies), 2)
        self.assertEqual(exception.suggested_policies[0]['policy_id'], 'p1')
