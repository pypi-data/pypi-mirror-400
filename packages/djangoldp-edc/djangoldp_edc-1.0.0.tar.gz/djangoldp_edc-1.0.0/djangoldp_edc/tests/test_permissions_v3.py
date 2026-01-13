"""
Tests for EdcContractPermissionV3 and related classes.
"""

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock
import json

from djangoldp_edc.permissions import (
    EdcContractPermissionV3,
    EdcContractPermissionV3WithFallback,
    EdcContractPermissionV3WithAutoNegotiation,
    EdcContractPermissionV3PolicyDiscovery,
)
from djangoldp_edc.exceptions import NegotiationRequired
from djangoldp_edc.tests.test_base import EdcTestCase, MockResponse


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
    EDC_API_KEY='test-api-key',
    EDC_AGREEMENT_VALIDATION_ENABLED=True,
)
class EdcContractPermissionV3TestCase(EdcTestCase):
    """Tests for EdcContractPermissionV3."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermissionV3()

    def test_denies_access_without_headers(self):
        """Test that access is denied when DSP headers are missing."""
        request = self.create_request()
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertFalse(result)

    def test_denies_access_with_only_agreement_header(self):
        """Test that access is denied when only agreement header is present."""
        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123'
        })
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertFalse(result)

    def test_denies_access_with_only_participant_header(self):
        """Test that access is denied when only participant header is present."""
        request = self.create_request(headers={
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertFalse(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_grants_access_with_valid_agreement(self, mock_get):
        """Test that access is granted with valid DSP headers and agreement."""
        agreement = self.create_mock_agreement()
        mock_get.return_value = MockResponse(agreement, 200)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertTrue(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_denies_access_with_invalid_agreement(self, mock_get):
        """Test that access is denied when agreement is not found."""
        mock_get.return_value = MockResponse({}, 404)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'invalid-agreement',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertFalse(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_denies_access_with_participant_mismatch(self, mock_get):
        """Test that access is denied when participant ID doesn't match."""
        agreement = self.create_mock_agreement(consumer_id='did:web:other:999')
        mock_get.return_value = MockResponse(agreement, 200)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertFalse(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_denies_access_with_asset_mismatch(self, mock_get):
        """Test that access is denied when asset ID doesn't match."""
        agreement = self.create_mock_agreement(asset_id='http://other-server/objects/other')
        mock_get.return_value = MockResponse(agreement, 200)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertFalse(result)

    def test_denies_unsafe_methods(self):
        """Test that unsafe methods (POST, PUT, DELETE) are denied."""
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            request = self.create_request(method=method, headers={
                'DSP-AGREEMENT-ID': 'test-agreement-123',
                'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
            })
            view = Mock()

            result = self.permission.has_permission(request, view)

            self.assertFalse(result, f"Expected {method} to be denied")

    @override_settings(EDC_AGREEMENT_VALIDATION_ENABLED=False)
    def test_allows_access_when_validation_disabled(self):
        """Test that access is granted when validation is disabled."""
        request = self.create_request()
        view = Mock()

        permission = EdcContractPermissionV3()
        result = permission.has_permission(request, view)

        self.assertTrue(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_subresource_access_granted(self, mock_get):
        """Test that access to subresources is granted when parent is covered."""
        agreement = self.create_mock_agreement(
            asset_id='http://localhost:8000/objects/trial6'
        )
        mock_get.return_value = MockResponse(agreement, 200)

        # Request for a subresource
        request = self.create_request(
            path='/objects/trial6/123/',
            headers={
                'DSP-AGREEMENT-ID': 'test-agreement-123',
                'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
            }
        )
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/123/')
        view = Mock()

        result = self.permission.has_permission(request, view)

        self.assertTrue(result)


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
    EDC_API_KEY='test-api-key',
)
class EdcContractPermissionV3WithFallbackTestCase(EdcTestCase):
    """Tests for EdcContractPermissionV3WithFallback."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermissionV3WithFallback()

    @patch('djangoldp_edc.utils.requests.get')
    def test_uses_header_validation_when_headers_present(self, mock_get):
        """Test that header-based validation is used when headers are present."""
        agreement = self.create_mock_agreement()
        mock_get.return_value = MockResponse(agreement, 200)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertTrue(result)

    @patch('djangoldp_edc.permissions.v3_fallback.requests.get')
    @patch('djangoldp_edc.permissions.v3_fallback.requests.post')
    def test_falls_back_to_user_profile_when_no_headers(self, mock_post, mock_get):
        """Test that user profile validation is used when headers are missing."""
        remote_user = self.create_mock_remote_user()
        mock_get.return_value = MockResponse(remote_user, 200)

        # Mock agreement query response
        mock_post.return_value = MockResponse([self.create_mock_agreement()], 200)

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertTrue(result)

    @patch('djangoldp_edc.permissions.v3_fallback.requests.get')
    def test_denies_access_when_user_has_no_dataspace_profile(self, mock_get):
        """Test that access is denied when user has no dataSpaceProfile."""
        remote_user = {'@id': 'http://example.com/users/1', 'dataSpaceProfile': None}
        mock_get.return_value = MockResponse(remote_user, 200)

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
    EDC_API_KEY='test-api-key',
    EDC_PROVIDER_DID='did:web:provider:456',
    EDC_AUTO_NEGOTIATION_ENABLED=True,
)
class EdcContractPermissionV3WithAutoNegotiationTestCase(EdcTestCase):
    """Tests for EdcContractPermissionV3WithAutoNegotiation."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermissionV3WithAutoNegotiation()

    @patch('djangoldp_edc.utils.requests.get')
    def test_grants_access_with_valid_agreement(self, mock_get):
        """Test that access is granted immediately with valid agreement."""
        agreement = self.create_mock_agreement()
        mock_get.return_value = MockResponse(agreement, 200)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertTrue(result)

    def test_denies_without_consumer_connector_url(self):
        """Test that access is denied when connector URL is missing for negotiation."""
        request = self.create_request(headers={
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)

    @patch('djangoldp_edc.permissions.v3_auto.requests.post')
    @patch('djangoldp_edc.utils.requests.post')
    def test_initiates_negotiation_when_no_agreement(self, mock_utils_post, mock_perm_post):
        """Test that negotiation is initiated when no agreement exists."""
        # Mock catalog response
        catalog = self.create_mock_catalog()
        mock_utils_post.return_value = MockResponse(catalog, 200)

        # Mock negotiation response
        mock_perm_post.return_value = MockResponse({'@id': 'negotiation-123'}, 200)

        request = self.create_request(headers={
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123',
            'DSP-CONSUMER-CONNECTORURL': 'http://consumer:8082/api/dsp'
        })
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        # Access is denied but negotiation should be initiated
        self.assertFalse(result)

    @override_settings(EDC_AUTO_NEGOTIATION_ENABLED=False)
    def test_denies_access_when_auto_negotiation_disabled(self):
        """Test that access is denied when auto-negotiation is disabled."""
        request = self.create_request(headers={
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123',
            'DSP-CONSUMER-CONNECTORURL': 'http://consumer:8082/api/dsp'
        })
        view = Mock()
        obj = Mock()

        permission = EdcContractPermissionV3WithAutoNegotiation()
        result = permission.has_object_permission(request, view, obj)

        self.assertFalse(result)


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
    EDC_API_KEY='test-api-key',
    EDC_POLICY_DISCOVERY_ENABLED=True,
)
class EdcContractPermissionV3PolicyDiscoveryTestCase(EdcTestCase):
    """Tests for EdcContractPermissionV3PolicyDiscovery."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermissionV3PolicyDiscovery()

    def test_denies_without_participant_id(self):
        """Test that access is denied when participant ID is missing."""
        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_grants_access_with_valid_agreement(self, mock_get):
        """Test that access is granted with valid agreement."""
        agreement = self.create_mock_agreement()
        mock_get.return_value = MockResponse(agreement, 200)

        request = self.create_request(headers={
            'DSP-AGREEMENT-ID': 'test-agreement-123',
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertTrue(result)

    @patch('djangoldp_edc.utils.requests.post')
    def test_raises_negotiation_required_when_no_agreement(self, mock_post):
        """Test that NegotiationRequired is raised when no agreement exists."""
        # The asset ID needs to match what get_asset_id_from_request generates
        # For the default slugify strategy on http://localhost:8000/objects/trial6/
        # The slugify function removes all non-alphanumeric characters (no dashes)
        catalog = self.create_mock_catalog(asset_id='http8000localhostobjectstrial6')
        mock_post.return_value = MockResponse(catalog, 200)

        request = self.create_request(headers={
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()
        obj = Mock()

        with self.assertRaises(NegotiationRequired) as context:
            self.permission.has_object_permission(request, view, obj)

        self.assertIsNotNone(context.exception.suggested_policies)
        self.assertEqual(context.exception.participant_id, 'did:web:consumer:123')

    @override_settings(EDC_POLICY_DISCOVERY_ENABLED=False)
    def test_denies_access_when_policy_discovery_disabled(self):
        """Test that access is denied when policy discovery is disabled."""
        request = self.create_request(headers={
            'DSP-PARTICIPANT-ID': 'did:web:consumer:123'
        })
        view = Mock()
        obj = Mock()

        permission = EdcContractPermissionV3PolicyDiscovery()
        result = permission.has_object_permission(request, view, obj)

        self.assertFalse(result)


class AssetIdGenerationTestCase(EdcTestCase):
    """Tests for asset ID generation strategies."""

    def test_slugify_strategy(self):
        """Test slugify asset ID generation."""
        permission = EdcContractPermissionV3()

        request = self.create_request(path='/objects/trial6/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/')

        with override_settings(EDC_ASSET_ID_STRATEGY='slugify'):
            asset_id = permission.get_asset_id(request)

        self.assertIn('localhost', asset_id)
        self.assertIn('objects', asset_id)
        self.assertIn('trial6', asset_id)

    def test_path_strategy(self):
        """Test path asset ID generation."""
        permission = EdcContractPermissionV3()

        request = self.create_request(path='/objects/trial6/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/')

        with override_settings(EDC_ASSET_ID_STRATEGY='path'):
            asset_id = permission.get_asset_id(request)

        self.assertEqual(asset_id, '/objects/trial6')

    def test_full_url_strategy(self):
        """Test full URL asset ID generation."""
        permission = EdcContractPermissionV3()

        request = self.create_request(path='/objects/trial6/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/')

        with override_settings(EDC_ASSET_ID_STRATEGY='full_url'):
            asset_id = permission.get_asset_id(request)

        self.assertEqual(asset_id, 'http://localhost:8000/objects/trial6')

    def test_container_strategy(self):
        """Test container asset ID generation."""
        permission = EdcContractPermissionV3()

        request = self.create_request(path='/objects/trial6/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/')

        with override_settings(EDC_ASSET_ID_STRATEGY='container'):
            asset_id = permission.get_asset_id(request)

        self.assertEqual(asset_id, 'trial6')

    def test_removes_numeric_resource_id(self):
        """Test that numeric resource IDs are removed from asset ID."""
        permission = EdcContractPermissionV3()

        request = self.create_request(path='/objects/trial6/123/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/123/')

        with override_settings(EDC_ASSET_ID_STRATEGY='path'):
            asset_id = permission.get_asset_id(request)

        self.assertEqual(asset_id, '/objects/trial6')
        self.assertNotIn('123', asset_id)
