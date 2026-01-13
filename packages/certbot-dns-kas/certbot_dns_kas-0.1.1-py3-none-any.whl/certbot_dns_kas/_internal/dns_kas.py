import logging
from typing import Any
from typing import Optional

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

try:
    from kasserver import KasServer
except ImportError:
    # Allow import for basic setuptools operations even if kasserver is missing
    KasServer = None

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for All-Inkl."""

    description = 'Obtain certificates using a DNS TXT record with All-Inkl (KAS).'
    # ttl = 60  # Library 'kasserver' does not support setting TTL via add_dns_record

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._kas_client = None

    @classmethod
    def add_parser_arguments(cls, add: Any, default_propagation_seconds: int = 120) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='All-Inkl KAS credentials INI file.')

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            'credentials',
            'All-Inkl credentials INI file',
            {
                'kas_user': 'KAS username/login',
                'kas_password': 'KAS password',
            }
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        # Note: 'record_aux' is typically priority. KAS API usually expects 0 for TXT.
        # TTL is not evidently exposed in add_dns_record signature (fqdn, record_type, record_data, record_aux).
        self._get_kas_client().add_dns_record(
            fqdn=validation_name,
            record_type='TXT',
            record_data=validation,
            record_aux=0
        )

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        client = self._get_kas_client()
        _, zone_name = client._split_fqdn(validation_name)
        
        try:
            # Safe Cleanup: Find the specific record ID matching the validation token
            records = client.get_dns_records(zone_name)
            record_id = None
            
            # The API returns 'prefix' for record_name, e.g. '_acme-challenge' for '_acme-challenge.example.com'
            # We must match both name and content to be sure.
            target_name = validation_name.removesuffix(f".{zone_name}")
            if target_name.endswith('.'):
                target_name = target_name[:-1]

            for item in records:
                if (item.get('name') == target_name and 
                    item.get('type') == 'TXT' and 
                    item.get('data') == validation):
                    record_id = item.get('id')
                    break
            
            if record_id:
                logger.info(f"Deleting TXT record for {validation_name} (ID: {record_id})")
                # accessing protected method _request to delete by ID, because
                # public delete_dns_record() is unsafe (deletes first match)
                client._request("delete_dns_settings", {"record_id": record_id})
            else:
                logger.warning(f"Could not find TXT record for {validation_name} to delete.")

        except Exception as e:
            logger.warning('Failed to delete DNS record: %s', e)

    def _get_kas_client(self) -> "KasServer":
        import os
        if not self._kas_client:
            if KasServer is None:
                raise errors.PluginError("kasserver library is not installed.")
            
            # kasserver uses environment variables for configuration.
            # We set them temporarily for instantiation and clear them immediately
            # to minimize side effects / leakage.
            env_user = self.credentials.conf('kas_user')
            env_pass = self.credentials.conf('kas_password')
            
            os.environ['KASSERVER_USER'] = env_user
            os.environ['KASSERVER_PASSWORD'] = env_pass
            
            try:
                self._kas_client = KasServer()
            finally:
                # Cleanup environment variables
                # We use pop with default None to avoid errors if they were already missing
                if os.environ.get('KASSERVER_USER') == env_user:
                     os.environ.pop('KASSERVER_USER', None)
                if os.environ.get('KASSERVER_PASSWORD') == env_pass:
                     os.environ.pop('KASSERVER_PASSWORD', None)

        return self._kas_client
