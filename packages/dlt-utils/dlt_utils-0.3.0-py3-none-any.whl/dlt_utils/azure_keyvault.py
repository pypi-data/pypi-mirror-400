"""
Azure Key Vault utilities voor secret management.

Dit module biedt een AzureKeyVault class voor het ophalen, opslaan en beheren van
secrets in Azure Key Vault. Authenticatie gebeurt via Service Principal credentials
(client_id, client_secret, tenant_id).

Gebruik:
    - Secrets ophalen voor database credentials, API keys, etc.
    - Secrets opslaan/updaten vanuit pipelines
    - Tags updaten voor secrets

Vereiste environment variables:
    - KEYVAULT_BASE_URL: URL van de Key Vault (bijv. https://myvault.vault.azure.net/)
    - KEYVAULT_SECRET_NAME: Naam van de secret
    - AZURE_TENANT_ID: Azure AD tenant ID
    - AZURE_CLIENT_ID: Service Principal client ID
    - AZURE_CLIENT_SECRET: Service Principal client secret
"""
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
import json
import os


class AzureKeyVault:
    def __init__(self):
        """
        Base class for Azure
        """
        super(AzureKeyVault, self).__init__()

        # Azure Key Vault configuration
        self.KEYVAULT_BASE_URL = os.getenv('KEYVAULT_BASE_URL')
        self.KEYVAULT_SECRET_NAME = os.getenv('KEYVAULT_SECRET_NAME')

        # Initialize Azure credential and Key Vault client
        self.credential = ClientSecretCredential(
            tenant_id=os.getenv('AZURE_TENANT_ID'),
            client_id=os.getenv('AZURE_CLIENT_ID'),
            client_secret=os.getenv('AZURE_CLIENT_SECRET')
        )
        self.secret_client = SecretClient(
            vault_url=self.KEYVAULT_BASE_URL,
            credential=self.credential
        )

    def get_secret(self) -> object:
        """
        Get secret from Azure Key Vault.

        Returns
        -------
        object
            Object with value, properties, etc. of the secret
        """
        secret = self.secret_client.get_secret(self.KEYVAULT_SECRET_NAME)

        return secret

    def update_secret_tags(self, tags: dict):
        """
        Update tags on the Key Vault secret.

        Parameters
        ----------
        tags : dict
            Dictionary of tags to set on the secret
        """
        self.secret_client.update_secret_properties(
            self.KEYVAULT_SECRET_NAME,
            tags=tags
        )
        print("Updated Key Vault tags successfully")

    def set_secret(self, secret_value: dict):
        """
        Set secret to Azure Key Vault.

        Parameters
        ----------
        secret_value : dict
            Secret value to set to Azure Key Vault
        """

        self.secret_client.set_secret(
            self.KEYVAULT_SECRET_NAME,
            json.dumps(secret_value),
            tags={}
        )
        print("Secret set to Key Vault successfully")


