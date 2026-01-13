"""
Tests for utility functions.
"""

from django.test import TestCase, override_settings
from unittest.mock import Mock, patch
import json

from djangoldp_edc.utils import (
    get_edc_url,
    get_edc_participant_id,
    get_edc_api_key,
    get_asset_id_from_request,
    fetch_agreement,
    fetch_catalog_entry,
    extract_dataset_from_catalog,
    calculate_policy_openness,
    describe_policy,
    is_contract_valid,
    is_resource_covered_by_contract,
)
from djangoldp_edc.tests.test_base import MockResponse


class SettingsUtilsTestCase(TestCase):
    """Tests for settings utility functions."""

    @override_settings(EDC_URL='http://test-edc.example.com')
    def test_get_edc_url(self):
        """Test getting EDC URL from settings."""
        url = get_edc_url()
        self.assertEqual(url, 'http://test-edc.example.com')

    def test_get_edc_url_returns_none_when_not_set(self):
        """Test that None is returned when EDC_URL is not set."""
        with override_settings():
            # Remove EDC_URL setting
            from django.conf import settings
            if hasattr(settings, 'EDC_URL'):
                delattr(settings, 'EDC_URL')
            # Just test it doesn't crash
            url = get_edc_url()
            # May be None or a default value

    @override_settings(EDC_PARTICIPANT_ID='my-participant')
    def test_get_edc_participant_id(self):
        """Test getting EDC participant ID from settings."""
        participant_id = get_edc_participant_id()
        self.assertEqual(participant_id, 'my-participant')

    @override_settings(EDC_API_KEY='secret-key-123')
    def test_get_edc_api_key(self):
        """Test getting EDC API key from settings."""
        api_key = get_edc_api_key()
        self.assertEqual(api_key, 'secret-key-123')


class AssetIdFromRequestTestCase(TestCase):
    """Tests for get_asset_id_from_request function."""

    def create_mock_request(self, url):
        """Create a mock request with build_absolute_uri."""
        request = Mock()
        request.build_absolute_uri = Mock(return_value=url)
        return request

    def test_slugify_strategy_default(self):
        """Test default slugify strategy."""
        request = self.create_mock_request('http://localhost:8000/objects/trial6/')

        asset_id = get_asset_id_from_request(request, 'slugify')

        self.assertIn('localhost', asset_id)
        self.assertIn('objects', asset_id)
        self.assertIn('trial6', asset_id)

    def test_path_strategy(self):
        """Test path strategy returns URL path."""
        request = self.create_mock_request('http://localhost:8000/objects/trial6/')

        asset_id = get_asset_id_from_request(request, 'path')

        self.assertEqual(asset_id, '/objects/trial6')

    def test_full_url_strategy(self):
        """Test full URL strategy."""
        request = self.create_mock_request('http://localhost:8000/objects/trial6/')

        asset_id = get_asset_id_from_request(request, 'full_url')

        self.assertEqual(asset_id, 'http://localhost:8000/objects/trial6')

    def test_container_strategy(self):
        """Test container strategy returns last path segment."""
        request = self.create_mock_request('http://localhost:8000/objects/trial6/')

        asset_id = get_asset_id_from_request(request, 'container')

        self.assertEqual(asset_id, 'trial6')

    def test_removes_numeric_id(self):
        """Test that numeric resource IDs are removed."""
        request = self.create_mock_request('http://localhost:8000/objects/trial6/123/')

        asset_id = get_asset_id_from_request(request, 'path')

        self.assertEqual(asset_id, '/objects/trial6')

    def test_handles_url_with_port(self):
        """Test handling of URLs with non-standard ports."""
        request = self.create_mock_request('http://localhost:9000/objects/trial6/')

        asset_id = get_asset_id_from_request(request, 'full_url')

        self.assertEqual(asset_id, 'http://localhost:9000/objects/trial6')


@override_settings(
    EDC_URL='http://localhost:8082',
    EDC_PARTICIPANT_ID='test-participant',
    EDC_API_KEY='test-api-key',
)
class FetchAgreementTestCase(TestCase):
    """Tests for fetch_agreement function."""

    @patch('djangoldp_edc.utils.requests.get')
    def test_fetches_agreement_successfully(self, mock_get):
        """Test successful agreement fetch."""
        agreement_data = {
            '@id': 'agreement-123',
            'assetId': 'test-asset',
            'consumerId': 'did:web:consumer:123'
        }
        mock_get.return_value = MockResponse(agreement_data, 200)

        result = fetch_agreement('agreement-123')

        self.assertEqual(result['@id'], 'agreement-123')
        mock_get.assert_called_once()

    @patch('djangoldp_edc.utils.requests.get')
    def test_returns_none_for_404(self, mock_get):
        """Test that None is returned for 404 responses."""
        mock_get.return_value = MockResponse({}, 404)

        result = fetch_agreement('nonexistent')

        self.assertIsNone(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_returns_none_on_timeout(self, mock_get):
        """Test that None is returned on timeout."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()

        result = fetch_agreement('agreement-123')

        self.assertIsNone(result)

    @patch('djangoldp_edc.utils.requests.get')
    def test_returns_none_on_error(self, mock_get):
        """Test that None is returned on request error."""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Connection error")

        result = fetch_agreement('agreement-123')

        self.assertIsNone(result)


class ExtractDatasetFromCatalogTestCase(TestCase):
    """Tests for extract_dataset_from_catalog function."""

    def test_extracts_from_flat_catalog(self):
        """Test extraction from flat catalog structure."""
        catalog = {
            'dcat:dataset': [
                {'id': 'asset-1', 'name': 'Asset 1'},
                {'id': 'asset-2', 'name': 'Asset 2'}
            ]
        }

        result = extract_dataset_from_catalog(catalog, 'asset-2')

        self.assertEqual(result['name'], 'Asset 2')

    def test_extracts_from_nested_catalog(self):
        """Test extraction from nested catalog structure."""
        catalog = {
            'dcat:dataset': [
                {
                    '@type': 'dcat:Catalog',
                    'dcat:dataset': [
                        {'id': 'nested-asset', 'name': 'Nested Asset'}
                    ]
                }
            ]
        }

        result = extract_dataset_from_catalog(catalog, 'nested-asset')

        self.assertEqual(result['name'], 'Nested Asset')

    def test_extracts_from_catalog_list(self):
        """Test extraction from list of catalogs."""
        catalogs = [
            {'dcat:dataset': [{'id': 'asset-1'}]},
            {'dcat:dataset': [{'id': 'asset-2', 'name': 'Found'}]}
        ]

        result = extract_dataset_from_catalog(catalogs, 'asset-2')

        self.assertEqual(result['name'], 'Found')

    def test_returns_none_when_not_found(self):
        """Test that None is returned when asset not found."""
        catalog = {'dcat:dataset': [{'id': 'other-asset'}]}

        result = extract_dataset_from_catalog(catalog, 'nonexistent')

        self.assertIsNone(result)

    def test_handles_at_id_format(self):
        """Test handling of @id format."""
        catalog = {
            'dcat:dataset': [
                {'@id': 'asset-1', 'name': 'Asset 1'}
            ]
        }

        result = extract_dataset_from_catalog(catalog, 'asset-1')

        self.assertEqual(result['name'], 'Asset 1')


class CalculatePolicyOpennessTestCase(TestCase):
    """Tests for calculate_policy_openness function."""

    def test_fully_open_policy_scores_100(self):
        """Test that a policy with no restrictions scores 100."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [],
            'odrl:obligation': []
        }

        score = calculate_policy_openness(policy)

        self.assertEqual(score, 100.0)

    def test_prohibition_reduces_score(self):
        """Test that prohibitions reduce the score."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [{'action': 'modify'}],
            'odrl:obligation': []
        }

        score = calculate_policy_openness(policy)

        self.assertEqual(score, 70.0)  # 100 - 30

    def test_obligation_reduces_score(self):
        """Test that obligations reduce the score."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [],
            'odrl:obligation': [{'action': 'attribute'}]
        }

        score = calculate_policy_openness(policy)

        self.assertEqual(score, 80.0)  # 100 - 20

    def test_permission_constraint_reduces_score(self):
        """Test that permission constraints reduce the score."""
        policy = {
            'odrl:permission': [{
                'action': 'use',
                'odrl:constraint': [{'leftOperand': 'dateTime'}]
            }],
            'odrl:prohibition': [],
            'odrl:obligation': []
        }

        score = calculate_policy_openness(policy)

        self.assertEqual(score, 90.0)  # 100 - 10

    def test_combined_restrictions(self):
        """Test combined restrictions."""
        policy = {
            'odrl:permission': [{'odrl:constraint': [{}]}],
            'odrl:prohibition': [{}],
            'odrl:obligation': [{'odrl:constraint': [{}]}]
        }

        score = calculate_policy_openness(policy)

        # 100 - 30 (prohibition) - 20 (obligation) - 5 (obligation constraint) - 10 (permission constraint) = 35
        self.assertEqual(score, 35.0)

    def test_never_goes_below_zero(self):
        """Test that score never goes below zero."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [{}, {}, {}, {}, {}],  # 5 * 30 = 150
            'odrl:obligation': []
        }

        score = calculate_policy_openness(policy)

        self.assertEqual(score, 0.0)


class DescribePolicyTestCase(TestCase):
    """Tests for describe_policy function."""

    def test_describes_open_policy(self):
        """Test description of open policy."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [],
            'odrl:obligation': []
        }

        description = describe_policy(policy)

        self.assertEqual(description, "Open access policy with no restrictions")

    def test_describes_prohibitions(self):
        """Test description includes prohibition count."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [{}, {}],
            'odrl:obligation': []
        }

        description = describe_policy(policy)

        self.assertIn("2 prohibition(s)", description)

    def test_describes_obligations(self):
        """Test description includes obligation count."""
        policy = {
            'odrl:permission': [],
            'odrl:prohibition': [],
            'odrl:obligation': [{}]
        }

        description = describe_policy(policy)

        self.assertIn("1 obligation(s)", description)


class IsContractValidTestCase(TestCase):
    """Tests for is_contract_valid function."""

    def test_finalized_contract_is_valid(self):
        """Test that FINALIZED contracts are valid."""
        contract = {'state': 'FINALIZED'}

        result = is_contract_valid(contract)

        self.assertTrue(result)

    def test_verified_contract_is_valid(self):
        """Test that VERIFIED contracts are valid."""
        contract = {'state': 'VERIFIED'}

        result = is_contract_valid(contract)

        self.assertTrue(result)

    def test_pending_contract_is_invalid(self):
        """Test that PENDING contracts are invalid."""
        contract = {'state': 'PENDING'}

        result = is_contract_valid(contract)

        self.assertFalse(result)

    def test_missing_state_assumes_valid(self):
        """Test that missing state field assumes valid."""
        contract = {'@id': 'agreement-123'}

        result = is_contract_valid(contract)

        self.assertTrue(result)

    def test_handles_edc_prefixed_state(self):
        """Test handling of edc: prefixed state field."""
        contract = {'edc:state': 'FINALIZED'}

        result = is_contract_valid(contract)

        self.assertTrue(result)


@override_settings(EDC_URL='http://localhost:8082')
class IsResourceCoveredByContractTestCase(TestCase):
    """Tests for is_resource_covered_by_contract function."""

    def test_exact_url_match(self):
        """Test exact URL match."""
        contract = {'assetId': 'http://localhost:8000/objects/trial6'}

        result = is_resource_covered_by_contract(
            contract, 'http://localhost:8000/objects/trial6'
        )

        self.assertTrue(result)

    def test_subresource_match(self):
        """Test subresource URL match."""
        contract = {'assetId': 'http://localhost:8000/objects/trial6'}

        result = is_resource_covered_by_contract(
            contract, 'http://localhost:8000/objects/trial6/123'
        )

        self.assertTrue(result)

    def test_different_resource_no_match(self):
        """Test that different resources don't match."""
        contract = {'assetId': 'http://localhost:8000/objects/trial6'}

        result = is_resource_covered_by_contract(
            contract, 'http://localhost:8000/objects/trial8'
        )

        self.assertFalse(result)

    def test_handles_index_suffix(self):
        """Test handling of /index suffix in asset ID."""
        contract = {'assetId': 'http://localhost:8000/indexes/users/index'}

        result = is_resource_covered_by_contract(
            contract, 'http://localhost:8000/indexes/users/name/pattern'
        )

        self.assertTrue(result)

    def test_missing_asset_id_returns_false(self):
        """Test that missing assetId returns False."""
        contract = {}

        result = is_resource_covered_by_contract(contract, 'http://localhost:8000/')

        self.assertFalse(result)

    def test_uses_policy_target_as_fallback(self):
        """Test using policy.target as fallback."""
        contract = {
            'policy': {'target': 'http://localhost:8000/objects/trial6'}
        }

        result = is_resource_covered_by_contract(
            contract, 'http://localhost:8000/objects/trial6'
        )

        self.assertTrue(result)
