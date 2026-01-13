"""
Base test utilities for djangoldp_edc tests.
"""

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock
import json


class MockResponse:
    """Mock HTTP response for requests library."""

    def __init__(self, json_data=None, status_code=200, text=''):
        self.json_data = json_data or {}
        self.status_code = status_code
        self.text = text or json.dumps(self.json_data)

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP Error: {self.status_code}")


class EdcTestCase(TestCase):
    """Base test case for EDC permission tests."""

    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Add urlid attribute for remote user lookup
        self.user.urlid = 'http://example.com/users/1'

    def create_request(self, method='GET', path='/objects/trial6/', user=None, headers=None):
        """Create a mock request with optional headers."""
        request_method = getattr(self.factory, method.lower())
        request = request_method(path)
        request.user = user or self.user

        # Add headers
        if headers:
            for key, value in headers.items():
                # Convert header name to META format
                meta_key = f"HTTP_{key.upper().replace('-', '_')}"
                request.META[meta_key] = value

        # Mock build_absolute_uri
        request.build_absolute_uri = Mock(return_value=f'http://localhost:8000{path}')

        return request

    def create_mock_agreement(self, agreement_id='test-agreement-123', asset_id='http://localhost:8000/objects/trial6', consumer_id='did:web:consumer:123'):
        """Create a mock EDC agreement response."""
        return {
            '@id': agreement_id,
            'assetId': asset_id,
            'consumerId': consumer_id,
            'providerId': 'did:web:provider:456',
            'state': 'FINALIZED',
            'contractSigningDate': '2025-01-01T00:00:00Z',
            'policy': {
                '@type': 'Offer',
                'target': asset_id
            }
        }

    def create_mock_catalog(self, asset_id='test-asset', policies=None):
        """Create a mock EDC catalog response."""
        if policies is None:
            policies = {
                '@id': 'policy-open-123',
                '@type': 'Offer',
                'odrl:permission': [],
                'odrl:prohibition': [],
                'odrl:obligation': []
            }

        return [{
            '@type': 'dcat:Catalog',
            'dcat:dataset': [{
                '@id': asset_id,
                'id': asset_id,
                'odrl:hasPolicy': policies
            }]
        }]

    def create_mock_remote_user(self, edc_api_key='test-api-key', edc_did='did:web:user:123'):
        """Create a mock remote user profile response."""
        return {
            '@id': 'http://example.com/users/1',
            'username': 'testuser',
            'dataSpaceProfile': {
                'edc_api_key': edc_api_key,
                'edc_did': edc_did
            }
        }
