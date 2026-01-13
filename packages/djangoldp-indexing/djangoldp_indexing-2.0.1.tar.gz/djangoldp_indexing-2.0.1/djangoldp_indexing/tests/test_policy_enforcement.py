"""Tests for policy enforcement and authorization."""

from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.core.exceptions import PermissionDenied
from rest_framework import status as http_status

from ..views.static import (
    check_dataspace_policy,
    verify_contract_agreement,
    is_contract_valid,
    is_resource_covered_by_contract,
)


class ContractBasedAuthorizationTest(TestCase):
    """Tests for contract-based authorization approach."""

    def setUp(self):
        """Set up test data and mocks."""
        self.factory = RequestFactory()
        self.test_url = '/indexes/users/index'
        self.contract_id = 'test-contract-123'
        self.participant_id = 'test-participant-456'

    def test_verify_contract_agreement_success(self):
        """Test successful contract verification."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = self.participant_id

        mock_contract_data = {
            'state': 'FINALIZED',
            'assetId': 'http://testserver/indexes/users/index',
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_contract_data
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"state": "FINALIZED", "assetId": "http://testserver/indexes/users/index"}'
            mock_get.return_value = mock_response

            result = verify_contract_agreement(request, self.contract_id)

            self.assertTrue(result)
            mock_get.assert_called_once()

    def test_verify_contract_agreement_missing_participant_id(self):
        """Test that missing DSP-PARTICIPANT-ID header raises PermissionDenied."""
        request = self.factory.get(self.test_url)

        with self.assertRaises(PermissionDenied) as context:
            verify_contract_agreement(request, self.contract_id)

        self.assertIn('DSP-PARTICIPANT-ID', str(context.exception))

    def test_verify_contract_agreement_invalid_state(self):
        """Test that invalid contract state raises PermissionDenied."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = self.participant_id

        mock_contract_data = {
            'state': 'PENDING',  # Invalid state
            'assetId': 'http://testserver/indexes/users/index',
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_contract_data
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"state": "PENDING", "assetId": "..."}'
            mock_get.return_value = mock_response

            with self.assertRaises(PermissionDenied) as context:
                verify_contract_agreement(request, self.contract_id)

            self.assertIn('not valid', str(context.exception))

    def test_verify_contract_agreement_resource_not_covered(self):
        """Test that uncovered resource raises PermissionDenied."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = self.participant_id

        mock_contract_data = {
            'state': 'FINALIZED',
            'assetId': 'http://testserver/indexes/other/index',  # Different resource
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_contract_data
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"state": "FINALIZED", "assetId": "http://testserver/indexes/other/index"}'
            mock_get.return_value = mock_response

            with self.assertRaises(PermissionDenied) as context:
                verify_contract_agreement(request, self.contract_id)

            self.assertIn('does not cover', str(context.exception))

    def test_verify_contract_agreement_not_found(self):
        """Test that 404 from EDC raises PermissionDenied."""
        import requests as real_requests

        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = self.participant_id

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = http_status.HTTP_404_NOT_FOUND
            mock_response.text = '{"error": "Not found"}'

            # Create a real HTTPError exception
            http_error = real_requests.exceptions.HTTPError(response=mock_response)
            http_error.response = mock_response
            mock_response.raise_for_status.side_effect = http_error

            mock_get.return_value = mock_response

            with self.assertRaises(PermissionDenied) as context:
                verify_contract_agreement(request, self.contract_id)

            self.assertIn('not found', str(context.exception).lower())

    def test_verify_contract_agreement_unauthorized(self):
        """Test that 401 from EDC raises PermissionDenied."""
        import requests as real_requests

        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = self.participant_id

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = http_status.HTTP_401_UNAUTHORIZED
            mock_response.text = '{"error": "Unauthorized"}'

            # Create a real HTTPError exception
            http_error = real_requests.exceptions.HTTPError(response=mock_response)
            http_error.response = mock_response
            mock_response.raise_for_status.side_effect = http_error

            mock_get.return_value = mock_response

            with self.assertRaises(PermissionDenied) as context:
                verify_contract_agreement(request, self.contract_id)

            self.assertIn('unauthorized', str(context.exception).lower())


class ContractValidationTest(TestCase):
    """Tests for contract validation helper functions."""

    def test_is_contract_valid_finalized(self):
        """Test that FINALIZED state is valid."""
        contract_data = {'state': 'FINALIZED'}
        self.assertTrue(is_contract_valid(contract_data))

    def test_is_contract_valid_verified(self):
        """Test that VERIFIED state is valid."""
        contract_data = {'state': 'VERIFIED'}
        self.assertTrue(is_contract_valid(contract_data))

    def test_is_contract_valid_invalid_states(self):
        """Test that invalid states return False."""
        invalid_states = ['PENDING', 'NEGOTIATING', 'TERMINATED', 'ERROR']
        for state in invalid_states:
            with self.subTest(state=state):
                contract_data = {'state': state}
                self.assertFalse(is_contract_valid(contract_data))

        # Empty string now returns True (assumes valid if no state)
        contract_data = {'state': ''}
        self.assertTrue(is_contract_valid(contract_data))

    def test_is_resource_covered_by_contract_exact_match(self):
        """Test exact URL match when assetId is a URL."""
        contract_data = {
            'assetId': 'http://testserver/indexes/users/index',
        }
        requested_url = 'http://testserver/indexes/users/index'

        self.assertTrue(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_subresource(self):
        """Test subresource access."""
        contract_data = {
            'assetId': 'http://testserver/indexes/users/index',
        }
        requested_url = 'http://testserver/indexes/users/title/index'

        self.assertTrue(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_policy_target(self):
        """Test policy target matching."""
        contract_data = {
            'assetId': '',
            'policy': {
                'target': 'http://testserver/indexes/users/index'
            }
        }
        requested_url = 'http://testserver/indexes/users/index'

        self.assertTrue(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_no_match(self):
        """Test that unrelated URLs return False."""
        contract_data = {
            'assetId': 'http://testserver/indexes/users/index',
        }
        requested_url = 'http://testserver/indexes/projects/index'

        self.assertFalse(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_asset_id_exact_match(self):
        """Test asset ID (non-URL) with exact baseUrl match."""
        contract_data = {
            'assetId': 'localtrial6index',
        }
        requested_url = 'http://testserver/indexes/objects/trial6/index'

        mock_asset_data = {
            'dataAddress': {
                'baseUrl': 'http://testserver/indexes/objects/trial6/index'
            }
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_asset_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            self.assertTrue(is_resource_covered_by_contract(contract_data, requested_url))

            # Verify asset endpoint was called
            call_args = mock_get.call_args
            self.assertIn('/management/v3/assets/localtrial6index', call_args[0][0])

    def test_is_resource_covered_by_contract_asset_id_subresource(self):
        """Test asset ID (non-URL) with subresource access."""
        contract_data = {
            'assetId': 'localtrial6index',
        }
        requested_url = 'http://testserver/indexes/objects/trial6/title/index'

        mock_asset_data = {
            'dataAddress': {
                'baseUrl': 'http://testserver/indexes/objects/trial6/index'
            }
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_asset_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            self.assertTrue(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_asset_id_no_match(self):
        """Test asset ID (non-URL) with no baseUrl match."""
        contract_data = {
            'assetId': 'localtrial6index',
        }
        requested_url = 'http://testserver/indexes/users/index'

        mock_asset_data = {
            'dataAddress': {
                'baseUrl': 'http://testserver/indexes/objects/trial6/index'
            }
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_asset_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            self.assertFalse(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_asset_id_missing_baseurl(self):
        """Test asset ID (non-URL) when asset has no baseUrl."""
        contract_data = {
            'assetId': 'localtrial6index',
        }
        requested_url = 'http://testserver/indexes/objects/trial6/index'

        mock_asset_data = {
            'dataAddress': {}
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_asset_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            self.assertFalse(is_resource_covered_by_contract(contract_data, requested_url))

    def test_is_resource_covered_by_contract_asset_fetch_error(self):
        """Test asset ID (non-URL) when asset fetch fails."""
        import requests as real_requests

        contract_data = {
            'assetId': 'nonexistent-asset',
        }
        requested_url = 'http://testserver/indexes/objects/trial6/index'

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404

            http_error = real_requests.exceptions.HTTPError(response=mock_response)
            http_error.response = mock_response
            mock_response.raise_for_status.side_effect = http_error

            mock_get.return_value = mock_response

            self.assertFalse(is_resource_covered_by_contract(contract_data, requested_url))


class TwoTierPolicyCheckTest(TestCase):
    """Tests for the two-tier policy check (contract + profile fallback)."""

    def setUp(self):
        """Set up test data and mocks."""
        self.factory = RequestFactory()
        self.test_url = '/indexes/users/index'
        self.contract_id = 'test-contract-123'
        self.participant_id = 'test-participant-456'

    def test_check_dataspace_policy_bypass_header(self):
        """Test that X-Bypass-Policy header bypasses all checks."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_X_BYPASS_POLICY'] = 'true'

        # Should not raise any exception
        check_dataspace_policy(request, None)

    def test_check_dataspace_policy_contract_success(self):
        """Test successful contract-based authorization."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_AGREEMENT_ID'] = self.contract_id
        request.META['HTTP_DSP_PARTICIPANT_ID'] = self.participant_id

        mock_contract_data = {
            'state': 'FINALIZED',
            'assetId': 'http://testserver/indexes/users/index',
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_contract_data
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"state": "FINALIZED", "assetId": "http://testserver/indexes/users/index"}'
            mock_get.return_value = mock_response

            # Should not raise any exception
            check_dataspace_policy(request, None)

    def test_check_dataspace_policy_contract_fails_no_fallback(self):
        """Test that when contract headers are provided but verification fails, we don't fall back."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_AGREEMENT_ID'] = self.contract_id
        # Missing participant ID will cause contract check to fail

        # With the new behavior, if contract headers are provided, we don't fall back
        # Instead, we raise PermissionDenied with the contract error
        with self.assertRaises(PermissionDenied) as context:
            check_dataspace_policy(request, None)

        # The error should mention contract-based authorization failure
        self.assertIn('Contract-based authorization failed', str(context.exception))
        self.assertIn('DSP-PARTICIPANT-ID', str(context.exception))

    def test_check_dataspace_policy_both_fail(self):
        """Test that PermissionDenied is raised when both approaches fail."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_AGREEMENT_ID'] = self.contract_id
        # Missing participant ID will cause contract check to fail

        mock_user = Mock()
        mock_user.is_authenticated = True
        mock_user.urlid = 'http://testserver/users/1'
        request.user = mock_user

        mock_catalog = []  # Empty catalog means no access

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_profile_response = Mock()
            mock_profile_response.json.return_value = {
                'dataSpaceProfile': {
                    'edc_api_key': 'test-key'
                }
            }

            with patch('djangoldp_indexing.views.static.requests.request') as mock_request:
                mock_catalog_response = Mock()
                mock_catalog_response.json.return_value = mock_catalog
                mock_catalog_response.raise_for_status = Mock()
                mock_request.return_value = mock_catalog_response

                mock_get.return_value = mock_profile_response

                with self.assertRaises(PermissionDenied):
                    check_dataspace_policy(request, None)

    def test_check_dataspace_policy_no_contract_header(self):
        """Test that missing contract header goes directly to profile-based."""
        request = self.factory.get(self.test_url)
        # No DSP-AGREEMENT-ID header

        mock_user = Mock()
        mock_user.is_authenticated = True
        mock_user.urlid = 'http://testserver/users/1'
        request.user = mock_user

        mock_catalog = [
            {
                'idx:IndexEntry': 'http://testserver/indexes/users/index'
            }
        ]

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_profile_response = Mock()
            mock_profile_response.json.return_value = {
                'dataSpaceProfile': {
                    'edc_api_key': 'test-key'
                }
            }

            with patch('djangoldp_indexing.views.static.requests.request') as mock_request:
                mock_catalog_response = Mock()
                mock_catalog_response.json.return_value = mock_catalog
                mock_catalog_response.raise_for_status = Mock()
                mock_request.return_value = mock_catalog_response

                mock_get.return_value = mock_profile_response

                # Should not raise exception
                check_dataspace_policy(request, None)


class HeaderNamingTest(TestCase):
    """Tests to ensure header names match djangoldp-tems convention."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.test_url = '/indexes/users/index'

    def test_dsp_agreement_id_header_name(self):
        """Test that DSP-AGREEMENT-ID is the correct header name."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_AGREEMENT_ID'] = 'test-contract'
        request.META['HTTP_DSP_PARTICIPANT_ID'] = 'test-participant'

        # This should be recognized
        contract_id = request.headers.get('DSP-AGREEMENT-ID')
        self.assertEqual(contract_id, 'test-contract')

    def test_dsp_participant_id_header_name(self):
        """Test that DSP-PARTICIPANT-ID is the correct header name."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = 'test-participant'

        # This should be recognized
        participant_id = request.headers.get('DSP-PARTICIPANT-ID')
        self.assertEqual(participant_id, 'test-participant')

    def test_verify_contract_uses_correct_header(self):
        """Test that verify_contract_agreement sends correct header to EDC."""
        request = self.factory.get(self.test_url)
        request.META['HTTP_DSP_PARTICIPANT_ID'] = 'test-participant'

        mock_contract_data = {
            'state': 'FINALIZED',
            'assetId': 'http://testserver/indexes/users/index',
        }

        with patch('djangoldp_indexing.views.static.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_contract_data
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"state": "FINALIZED", "assetId": "http://testserver/indexes/users/index"}'
            mock_get.return_value = mock_response

            verify_contract_agreement(request, 'test-contract')

            # Verify the header was sent to EDC
            call_args = mock_get.call_args
            headers_sent = call_args[1]['headers']
            self.assertEqual(headers_sent['DSP-PARTICIPANT-ID'], 'test-participant')
