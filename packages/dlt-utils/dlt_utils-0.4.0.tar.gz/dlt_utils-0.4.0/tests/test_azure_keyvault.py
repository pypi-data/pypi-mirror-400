"""Tests for Azure Key Vault utilities."""
import json
import os
from unittest.mock import MagicMock, patch

import pytest


class TestAzureKeyVault:
    """Test cases for AzureKeyVault class."""

    @patch.dict(os.environ, {
        'KEYVAULT_BASE_URL': 'https://test-vault.vault.azure.net/',
        'KEYVAULT_SECRET_NAME': 'test-secret',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_CLIENT_SECRET': 'test-client-secret'
    })
    @patch('dlt_utils.azure_keyvault.SecretClient')
    @patch('dlt_utils.azure_keyvault.ClientSecretCredential')
    def test_init(self, mock_credential, mock_secret_client):
        """Test AzureKeyVault initialization."""
        from dlt_utils.azure_keyvault import AzureKeyVault
        
        kv = AzureKeyVault()
        
        # Verify credential was created with correct parameters
        mock_credential.assert_called_once_with(
            tenant_id='test-tenant-id',
            client_id='test-client-id',
            client_secret='test-client-secret'
        )
        
        # Verify SecretClient was created
        mock_secret_client.assert_called_once()
        assert kv.KEYVAULT_BASE_URL == 'https://test-vault.vault.azure.net/'
        assert kv.KEYVAULT_SECRET_NAME == 'test-secret'

    @patch.dict(os.environ, {
        'KEYVAULT_BASE_URL': 'https://test-vault.vault.azure.net/',
        'KEYVAULT_SECRET_NAME': 'test-secret',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_CLIENT_SECRET': 'test-client-secret'
    })
    @patch('dlt_utils.azure_keyvault.SecretClient')
    @patch('dlt_utils.azure_keyvault.ClientSecretCredential')
    def test_get_secret(self, mock_credential, mock_secret_client):
        """Test getting a secret from Key Vault."""
        from dlt_utils.azure_keyvault import AzureKeyVault
        
        # Setup mock
        mock_secret = MagicMock()
        mock_secret.value = '{"key": "value"}'
        mock_secret_client.return_value.get_secret.return_value = mock_secret
        
        kv = AzureKeyVault()
        result = kv.get_secret()
        
        # Verify get_secret was called with correct secret name
        kv.secret_client.get_secret.assert_called_once_with('test-secret')
        assert result == mock_secret

    @patch.dict(os.environ, {
        'KEYVAULT_BASE_URL': 'https://test-vault.vault.azure.net/',
        'KEYVAULT_SECRET_NAME': 'test-secret',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_CLIENT_SECRET': 'test-client-secret'
    })
    @patch('dlt_utils.azure_keyvault.SecretClient')
    @patch('dlt_utils.azure_keyvault.ClientSecretCredential')
    def test_update_secret_tags(self, mock_credential, mock_secret_client):
        """Test updating secret tags."""
        from dlt_utils.azure_keyvault import AzureKeyVault
        
        kv = AzureKeyVault()
        tags = {'environment': 'test', 'version': '1.0'}
        kv.update_secret_tags(tags)
        
        # Verify update_secret_properties was called
        kv.secret_client.update_secret_properties.assert_called_once_with(
            'test-secret',
            tags=tags
        )

    @patch.dict(os.environ, {
        'KEYVAULT_BASE_URL': 'https://test-vault.vault.azure.net/',
        'KEYVAULT_SECRET_NAME': 'test-secret',
        'AZURE_TENANT_ID': 'test-tenant-id',
        'AZURE_CLIENT_ID': 'test-client-id',
        'AZURE_CLIENT_SECRET': 'test-client-secret'
    })
    @patch('dlt_utils.azure_keyvault.SecretClient')
    @patch('dlt_utils.azure_keyvault.ClientSecretCredential')
    def test_set_secret(self, mock_credential, mock_secret_client):
        """Test setting a secret in Key Vault."""
        from dlt_utils.azure_keyvault import AzureKeyVault
        
        kv = AzureKeyVault()
        secret_value = {'database': 'prod', 'password': 'secret123'}
        kv.set_secret(secret_value)
        
        # Verify set_secret was called with correct parameters
        kv.secret_client.set_secret.assert_called_once_with(
            'test-secret',
            json.dumps(secret_value),
            tags={}
        )


class TestAzureKeyVaultMissingEnvVars:
    """Test AzureKeyVault behavior with missing environment variables."""

    @patch.dict(os.environ, {}, clear=True)
    @patch('dlt_utils.azure_keyvault.SecretClient')
    @patch('dlt_utils.azure_keyvault.ClientSecretCredential')
    def test_init_missing_env_vars(self, mock_credential, mock_secret_client):
        """Test initialization with missing environment variables."""
        from dlt_utils.azure_keyvault import AzureKeyVault
        
        kv = AzureKeyVault()
        
        # Should initialize but with None values
        assert kv.KEYVAULT_BASE_URL is None
        assert kv.KEYVAULT_SECRET_NAME is None
