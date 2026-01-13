import sys
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

# from certbot.plugins import dns_test_common
# from certbot.plugins import dns_common_test
# from certbot.tests import util as test_util

from certbot_dns_kas._internal.dns_kas import Authenticator

class AuthenticatorTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.config = mock.MagicMock(dns_allinkl_credentials='path/to/credentials.ini')
        self.auth = Authenticator(self.config, 'dns-allinkl')
        
        self.auth.credentials = mock.MagicMock()
        self.auth.credentials.conf.side_effect = lambda x: 'mock_value'

        self.mock_client = mock.MagicMock()
        # Mock the _kas_client property or the class instantiation
        self.auth._kas_client = self.mock_client

    def test_perform(self):
        self.auth._perform('example.com', '_acme-challenge.example.com', 'token')
        self.mock_client.add_dns_record.assert_called_with(
            fqdn='_acme-challenge.example.com',
            record_type='TXT',
            record_data='token',
            record_aux=0
        )

    def test_cleanup_found(self):
        # Setup: Mock get_dns_records to return a match
        self.mock_client.get_dns_records.return_value = [
            {'name': '_acme-challenge', 'type': 'MX', 'data': 'other', 'id': '99'},
            {'name': '_acme-challenge', 'type': 'TXT', 'data': 'token', 'id': '123'},
            {'name': 'other', 'type': 'TXT', 'data': 'token', 'id': '456'},
        ]
        self.mock_client._split_fqdn.return_value = ('_acme-challenge', 'example.com')

        self.auth._cleanup('example.com', '_acme-challenge.example.com', 'token')
        
        # Verify loop logic found the right one
        self.mock_client.get_dns_records.assert_called_with('example.com')
        # Expect _request to be called with ID 123
        self.mock_client._request.assert_called_with(
            "delete_dns_settings", {"record_id": "123"}
        )

    def test_cleanup_not_found(self):
        # Setup: No match
        self.mock_client.get_dns_records.return_value = []
        self.mock_client._split_fqdn.return_value = ('_acme-challenge', 'example.com')

        self.auth._cleanup('example.com', '_acme-challenge.example.com', 'token')
        
        self.mock_client._request.assert_not_called()

    @mock.patch('certbot_dns_kas._internal.dns_kas.KasServer')
    @mock.patch.dict('os.environ', {}, clear=True)
    def test_get_kas_client(self, mock_kas):
        self.auth._kas_client = None
        self.auth._get_kas_client()
        
        import os
        # Verify credentials were used during init (via mock expectation if feasible, or relying on logic below)
        # But crucially, verify they are GONE after the call
        self.assertIsNone(os.environ.get('KASSERVER_USER'))
        self.assertIsNone(os.environ.get('KASSERVER_PASSWORD'))
        mock_kas.assert_called_once()


if __name__ == '__main__':
    unittest.main()
