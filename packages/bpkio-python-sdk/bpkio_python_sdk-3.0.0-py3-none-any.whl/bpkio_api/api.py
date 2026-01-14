import base64
import datetime
import json
import os
import time
from typing import Optional
from urllib.parse import urlparse

from uplink.auth import BearerToken

from bpkio_api.caching import init_cache
from bpkio_api.consumer import BpkioSdkConsumer
from bpkio_api.credential_provider import TenantProfile, TenantProfileProvider
from bpkio_api.defaults import DEFAULT_FQDN
from bpkio_api.endpoints import (
    CategoriesApi,
    ConsumptionApi,
    ServicesApi,
    SourcesApi,
    TenantsApi,
    TranscodingProfilesApi,
    UsersApi,
)
from bpkio_api.endpoints.login import LoginApi
from bpkio_api.exceptions import (
    BroadpeakIoApiError,
    ExpiredApiKeyFormat,
    InvalidApiKeyFormat,
    InvalidEndpointError,
    InvalidTenantError,
    MissingApiKeyError,
)
from bpkio_api.helpers.recorder import SessionRecorder
from bpkio_api.mappings import model_to_endpoint
from bpkio_api.models import Tenant


class BroadpeakIoApi(BpkioSdkConsumer):
    def __init__(
        self,
        *,
        tenant: Optional[str] = None,
        api_key: Optional[str] = None,
        fqdn: str = DEFAULT_FQDN,
        use_cache: bool = True,
        session_file: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Broadpeak.io API client.

        You can specify either a tenant label or an API key.
        If you specify a tenant label, the API key will be retrieved from the `~/.bpkio/tenant` file.

        If you don't specify either, the SDK will use environment variables `BPKIO_TENANT` or `BPKIO_API_KEY`.
        If those are not set, the SDK will check whether there is a default tenant configured in the `~/.bpkio/tenant` file.

        See the [Authentication](../guides/authentication.md) guide for more information.

        Args:
            tenant: The label of the Tenant Profile to use (from the `~/.bpkio/tenant` file).
            api_key: The tenant's API key.
            fqdn: The FQDN of the Broadpeak.io entrypoint to use.
            use_cache: Whether to use the cache.
            session_file: The file to record the session to.
        """
        self.use_cache = use_cache
        if tenant and api_key:
            raise ValueError("You can't specify both tenant and api_key")

        if fqdn and fqdn != DEFAULT_FQDN:
            fqdn = BroadpeakIoApi.normalise_fqdn(fqdn)

        tp = TenantProfileProvider()

        if tenant:
            if isinstance(tenant, str):
                t = tp.get_tenant_profile(tenant)
            if isinstance(tenant, TenantProfile):
                t = tenant
            self._api_key = t.api_key
            self._fqdn = t.fqdn

        elif api_key:
            self._api_key = api_key
            self._fqdn = fqdn or DEFAULT_FQDN

        elif os.environ.get("BPKIO_TENANT"):
            t = tp.get_tenant_profile(os.environ.get("BPKIO_TENANT"))
            self._api_key = t.api_key
            self._fqdn = t.fqdn

        elif os.environ.get("BPKIO_API_KEY"):
            self._api_key = os.environ.get("BPKIO_API_KEY")
            self._fqdn = os.environ.get("BPKIO_FQDN") or DEFAULT_FQDN

        elif tp.has_default_tenant():
            t = tp.get_tenant_profile("default")
            self._api_key = t.api_key
            self._fqdn = t.fqdn

        else:
            raise InvalidTenantError(
                "You must specify either api_key or tenant, "
                "or have configured a default tenant"
            )

        # Check if API key is missing
        if not self._api_key:
            raise MissingApiKeyError()

        base_url = f"https://{self._fqdn}/v1/"

        super().__init__(base_url, auth=BearerToken(self._api_key), **kwargs)

        tenant_id = self.get_tenant_id()
        if use_cache:
            init_cache(self.fqdn, tenant_id)

        self.session_recorder = SessionRecorder(session_file)

        self.sources = SourcesApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.services = ServicesApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.tenants = TenantsApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.users = UsersApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.transcoding_profiles = TranscodingProfilesApi(
            base_url, auth=BearerToken(self._api_key), **kwargs
        )
        self.consumption = ConsumptionApi(
            base_url, auth=BearerToken(self._api_key), **kwargs
        )
        self.categories = CategoriesApi(
            base_url, auth=BearerToken(self._api_key), **kwargs
        )
        self.login = LoginApi(base_url, auth=None, **kwargs)

        # Optional endpoints
        try:
            from bpkio_api_admin.addons import add_admin_endpoints

            add_admin_endpoints(
                self, base_url, auth=BearerToken(self._api_key), **kwargs
            )
        except ImportError:
            # Admin module is optional and may not be installed
            pass
        except Exception:
            # Other errors are silently ignored for optional admin endpoints
            pass

    @staticmethod
    def _parse_api_key(candidate: str) -> dict:
        """Parses an API Key (token) and extract the information it contains.

        Args:
            candidate (str): The API key

        Returns:
            dict: The content of the API key
        """
        try:
            parts = candidate.split(".")
            # Padding is required. Length doesn't matter provided it's long enough
            base64_bytes = parts[1] + "========"
            s = base64.b64decode(base64_bytes).decode("utf-8")
            payload = json.loads(s)
            # self.logger.debug("API Key payload: " + str(payload))

            # check expiration date
            if payload.get("exp") and payload.get("exp") < time.time():
                raise ExpiredApiKeyFormat(reason="API key expired")

            return payload

        except ExpiredApiKeyFormat as e:
            raise e
        except Exception as e:
            raise InvalidApiKeyFormat(reason=e)

    def parse_api_key(self) -> dict:
        """Parses the API Key and extracts the information it contains"""
        return self._parse_api_key(self._api_key)

    @staticmethod
    def is_valid_api_key_format(string: str):
        """Checks if the API Key is in the format expected by broadpeak.io"""
        try:
            BroadpeakIoApi._parse_api_key(string)
            return True
        except Exception:
            return False

    @staticmethod
    def is_expired_api_key(string: str):
        """Checks if the API Key is expired"""
        try:
            BroadpeakIoApi._parse_api_key(string)
            return False
        except ExpiredApiKeyFormat:
            return True

    def get_tenant_id(self) -> int:
        """Returns the tenant ID from the API Key"""
        apikey_info = self.parse_api_key()
        tenant_id = apikey_info.get("tenantId")
        if not tenant_id:
            # try to get the tenant ID from the API key payload,
            # by getting the value from any key ending with /tenant_id (allowing for multi-platform support)
            tenant_id = next(
                (
                    value
                    for key, value in apikey_info.items()
                    if key.endswith("/tenant_id")
                ),
                None,
            )

        return tenant_id

    @SessionRecorder.do_not_record
    def get_self_tenant(self) -> Tenant:
        """Returns the Tenant resource linked to the current API Key"""
        tenant_id = self.get_tenant_id()

        # Yet another workaround because /tenants/me does not work for Tenant 1
        if tenant_id == 1:
            tenant = Tenant(
                id=1,
                name="Tenant 1",
                description="Tenant 1",
                commercialPlan="ADMIN",
                state="enabled",
                creationDate=datetime.datetime.min,
                updateDate=datetime.datetime.min,
            )
        else:
            tenant = self.tenants.retrieve_self()
            # Necessary workaround because endpoint /tenants/me does not return the tenant ID anymore
            tenant.id = tenant_id

        tenant._fqdn = self.fqdn
        return tenant

    @property
    def fqdn(self):
        """Get the FQDN of the Broadpeak.io entrypoint"""
        return self._fqdn

    def uses_default_fqdn(self):
        """Check if the FQDN is the default one"""
        return self._fqdn == DEFAULT_FQDN

    @staticmethod
    def normalise_fqdn(url):
        """A function to allow extraction and normalisation of a FQDN from a full URL"""
        fqdn = url
        if url.startswith("http"):
            fqdn = urlparse(url).netloc

        if fqdn.startswith("app"):
            fqdn = "api" + fqdn[3:]

        if fqdn.startswith("login"):
            fqdn = "api" + fqdn[5:]

        return fqdn

    @staticmethod
    def is_correct_entrypoint(url: str, api_key: str, verify_ssl) -> bool | str:
        """Checks whether a URL is a valid Broadpeak.io entrypoint

        Args:
            url: The URL to check.
            api_key: The API key to use.
            verify_ssl: Whether to verify the SSL certificate.

        Returns:
            bool: True if the URL is a valid Broadpeak.io entrypoint, False otherwise.
        """
        try:
            api = BroadpeakIoApi(api_key=api_key, fqdn=url, verify_ssl=verify_ssl)
            api.get_self_tenant()
            return True
        except Exception:
            return False

    def test_access(self) -> bool:
        """Tests if the API key allows to access the API"""
        tenant_id = self.get_tenant_id()
        try:
            if tenant_id == 1:
                self.users.list()
            else:
                self.tenants.retrieve_self()
        except BroadpeakIoApiError:
            raise BroadpeakIoApiError(
                500,
                f"Unable to access the API for tenant {tenant_id} (on {self.fqdn}). Check that your API key is valid",
                None,
                None,
            )

    # -- API traversal methods

    def root_endpoint_for_resource(self, resource: object) -> object:
        """Returns the root endpoint for a given resource"""
        return model_to_endpoint(api=self, model=type(resource))

    def get_endpoint_from_path(self, path: list):
        try:
            endpoint = self
            for p in path:
                endpoint = getattr(endpoint, p)
            return endpoint
        except AttributeError as e:
            raise InvalidEndpointError(
                "The endpoint you are trying to access does not exist or is restricted",
                original_message=e.args[0],
            )
