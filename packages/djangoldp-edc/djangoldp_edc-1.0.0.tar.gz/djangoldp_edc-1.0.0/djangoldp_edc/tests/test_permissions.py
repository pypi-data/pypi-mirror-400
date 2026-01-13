"""
Tests for EdcContractPermission (original implementation).
"""

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock
import json

from djangoldp_edc.permissions import EdcContractPermission
from djangoldp_edc.tests.test_base import EdcTestCase, MockResponse


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
)
class EdcContractPermissionTestCase(EdcTestCase):
    """Tests for EdcContractPermission (original implementation)."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermission()

    def test_denies_unsafe_methods(self):
        """Test that unsafe methods are denied."""
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            request = self.create_request(method=method)
            view = Mock()
            obj = Mock()

            result = self.permission.has_object_permission(request, view, obj)

            self.assertFalse(result, f"Expected {method} to be denied")

    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_denies_access_when_user_has_no_urlid(self, mock_get):
        """Test that access is denied when user has no urlid attribute."""
        User = get_user_model()
        user_without_urlid = User.objects.create_user(
            username='nourl',
            email='nourl@example.com',
            password='testpass123'
        )
        # Remove urlid attribute
        if hasattr(user_without_urlid, 'urlid'):
            delattr(user_without_urlid, 'urlid')

        request = self.create_request(user=user_without_urlid)
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)

    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_denies_access_when_remote_user_has_no_dataspace_profile(self, mock_get):
        """Test that access is denied when remote user has no dataSpaceProfile."""
        remote_user = {'@id': 'http://example.com/users/1', 'dataSpaceProfile': None}
        mock_get.return_value = MockResponse(remote_user, 200)

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)

    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_denies_access_when_remote_user_has_no_api_key(self, mock_get):
        """Test that access is denied when user has no edc_api_key."""
        remote_user = {
            '@id': 'http://example.com/users/1',
            'dataSpaceProfile': {
                'edc_api_key': None,
                'edc_did': 'did:web:user:123'
            }
        }
        mock_get.return_value = MockResponse(remote_user, 200)

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)

    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_denies_access_when_remote_user_has_no_did(self, mock_get):
        """Test that access is denied when user has no edc_did."""
        remote_user = {
            '@id': 'http://example.com/users/1',
            'dataSpaceProfile': {
                'edc_api_key': 'test-key',
                'edc_did': None
            }
        }
        mock_get.return_value = MockResponse(remote_user, 200)

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)

    @patch('djangoldp_edc.permissions.base.requests.request')
    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_grants_access_with_existing_agreement(self, mock_get, mock_request):
        """Test that access is granted when user has existing agreement."""
        remote_user = self.create_mock_remote_user()
        mock_get.return_value = MockResponse(remote_user, 200)

        # Mock agreement query - returns list with one agreement
        mock_request.return_value = MockResponse([self.create_mock_agreement()], 200)

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertTrue(result)

    @patch('djangoldp_edc.permissions.base.requests.post')
    @patch('djangoldp_edc.permissions.base.requests.request')
    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_initiates_negotiation_when_no_agreement(self, mock_get, mock_request, mock_post):
        """Test that negotiation is initiated when no agreement exists."""
        remote_user = self.create_mock_remote_user()
        mock_get.return_value = MockResponse(remote_user, 200)

        # Mock agreement query - returns empty list
        mock_request.return_value = MockResponse([], 200)

        # Mock catalog response for policy retrieval
        catalog = self.create_mock_catalog()
        mock_post.side_effect = [
            MockResponse(catalog, 200),  # Catalog request
            MockResponse({'@id': 'negotiation-123'}, 200)  # Negotiation request
        ]

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        # Access is denied but negotiation is initiated
        self.assertFalse(result)

    @patch('djangoldp_edc.permissions.base.requests.get')
    def test_handles_remote_user_fetch_error(self, mock_get):
        """Test that errors in fetching remote user are handled gracefully."""
        mock_get.side_effect = Exception("Network error")

        request = self.create_request()
        view = Mock()
        obj = Mock()

        result = self.permission.has_object_permission(request, view, obj)

        self.assertFalse(result)


class GetAssetIdTestCase(EdcTestCase):
    """Tests for asset ID extraction from request."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermission()

    def test_extracts_asset_id_from_path(self):
        """Test that asset ID is correctly extracted from request path."""
        request = self.create_request(path='/objects/trial6/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/')

        asset_id = self.permission.get_asset_id(request)

        # Asset ID should be slugified version of URL
        self.assertIsInstance(asset_id, str)
        self.assertIn('localhost', asset_id)

    def test_removes_resource_id_from_path(self):
        """Test that numeric resource IDs are removed."""
        request = self.create_request(path='/objects/trial6/123/')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6/123/')

        asset_id = self.permission.get_asset_id(request)

        # 123 should not be in the asset ID
        self.assertNotIn('123', asset_id)

    def test_handles_path_without_trailing_slash(self):
        """Test handling of paths without trailing slash."""
        request = self.create_request(path='/objects/trial6')
        request.build_absolute_uri = Mock(return_value='http://localhost:8000/objects/trial6')

        asset_id = self.permission.get_asset_id(request)

        self.assertIsInstance(asset_id, str)
        self.assertTrue(len(asset_id) > 0)


class PolicyRetrievalTestCase(EdcTestCase):
    """Tests for policy retrieval from catalog."""

    def setUp(self):
        super().setUp()
        self.permission = EdcContractPermission()

    @patch('djangoldp_edc.permissions.base.requests.post')
    def test_retrieves_policy_from_flat_catalog(self, mock_post):
        """Test policy retrieval from flat catalog structure."""
        catalog = [{
            'dcat:dataset': [{
                'id': 'test-asset',
                'odrl:hasPolicy': {'@id': 'policy-123'}
            }]
        }]
        mock_post.return_value = MockResponse(catalog, 200)

        remote_user = self.create_mock_remote_user()
        policy_id = self.permission.get_policy_id_for_asset('test-asset', remote_user)

        self.assertEqual(policy_id, 'policy-123')

    @patch('djangoldp_edc.permissions.base.requests.post')
    def test_retrieves_policy_from_nested_catalog(self, mock_post):
        """Test policy retrieval from nested catalog structure."""
        catalog = [{
            'dcat:dataset': [{
                '@type': 'dcat:Catalog',
                'dcat:dataset': [{
                    'id': 'test-asset',
                    'odrl:hasPolicy': {'@id': 'nested-policy-456'}
                }]
            }]
        }]
        mock_post.return_value = MockResponse(catalog, 200)

        remote_user = self.create_mock_remote_user()
        policy_id = self.permission.get_policy_id_for_asset('test-asset', remote_user)

        self.assertEqual(policy_id, 'nested-policy-456')

    @patch('djangoldp_edc.permissions.base.requests.post')
    def test_returns_none_when_asset_not_found(self, mock_post):
        """Test that None is returned when asset is not in catalog."""
        catalog = [{
            'dcat:dataset': [{
                'id': 'other-asset',
                'odrl:hasPolicy': {'@id': 'policy-123'}
            }]
        }]
        mock_post.return_value = MockResponse(catalog, 200)

        remote_user = self.create_mock_remote_user()
        policy_id = self.permission.get_policy_id_for_asset('test-asset', remote_user)

        self.assertIsNone(policy_id)

    @patch('djangoldp_edc.permissions.base.requests.post')
    def test_handles_catalog_fetch_error(self, mock_post):
        """Test that errors in fetching catalog are handled gracefully."""
        mock_post.side_effect = Exception("Network error")

        remote_user = self.create_mock_remote_user()
        policy_id = self.permission.get_policy_id_for_asset('test-asset', remote_user)

        self.assertIsNone(policy_id)
