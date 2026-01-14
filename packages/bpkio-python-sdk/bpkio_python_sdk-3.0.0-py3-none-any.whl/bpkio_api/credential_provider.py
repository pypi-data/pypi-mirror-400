import configparser
import functools
import json
import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from configparser import SectionProxy
from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import Optional

from loguru import logger

from bpkio_api.defaults import DEFAULT_FQDN


def _get_bpkio_home() -> Path:
    """
    Get the bpkio home directory path.

    Checks for BPKIO_HOME environment variable first, then falls back to ~/.bpkio.

    Returns:
        Path: The bpkio home directory path
    """
    bpkio_home = os.getenv("BPKIO_HOME")
    if bpkio_home:
        return Path(bpkio_home).expanduser()
    return Path.home() / ".bpkio"


DEFAULT_INI_FILE = str(_get_bpkio_home() / "tenants")


class TenantCredentialProvider(ABC):
    def __init__(self, *args, **kwargs):
        self.source = "NA"

    @abstractmethod
    def get_api_key(self):
        pass

    @abstractmethod
    def get_username(self):
        pass

    @abstractmethod
    def get_password(self):
        pass

    def get_fqdn(self) -> Optional[str]:
        """Get the FQDN for the tenant. Returns None to use default.

        This method is optional - if not overridden, returns None to use DEFAULT_FQDN.
        """
        return None

    @abstractmethod
    def store_info(self, info: dict) -> dict:
        """Store credentials and return the modified config to save in the tenant list"""
        pass

    def store_credentials(self, info: dict) -> dict:
        """Alias for store_info(), kept for readability at call-sites.

        The intent is: store provider-owned secrets (e.g., in 1Password) and return the
        remaining entries that should be persisted in the tenant config file.
        """
        return self.store_info(info)


class TenantCredentialProviderFromConfigFile(TenantCredentialProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_info: SectionProxy = kwargs.get("tenant_info")
        self.source = "config"

    def get_api_key(self):
        return self.tenant_info.get("api_key")

    def get_username(self):
        return self.tenant_info.get("username")

    def get_password(self):
        return self.tenant_info.get("password")

    def get_fqdn(self) -> Optional[str]:
        """Get FQDN from config file. Returns None if not set (will use DEFAULT_FQDN)."""
        return self.tenant_info.get("fqdn")

    def store_info(self, info: dict):
        # Just return the credentials as-is since we're storing directly in config
        return info


class TenantCredentialProviderFrom1Password(TenantCredentialProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = "1Password"
        self.item_ref = kwargs.get("item_ref")
        if self.item_ref is not None:
            self.item_ref = self.item_ref.strip('"')

            self.item_id = self.item_ref.split("/")[3]
            self.vault_name = self.item_ref.split("/")[2]
            if "@" in self.vault_name:
                self.account_uuid = self.vault_name.split("@")[1]
                self.vault_name = self.vault_name.split("@")[0]
            else:
                self.account_uuid = None

        if "item" in kwargs:
            self.item = kwargs.get("item")
        else:
            self.item = None

    def get_api_key(self):
        try:
            return self._get_item_field("api key")
        except ValueError:
            try:
                return self._get_item_field("api_key")
            except ValueError:
                return None

    def get_username(self):
        try:
            return self._get_item_field("username")
        except ValueError:
            return None

    def get_password(self):
        try:
            return self._get_item_field("password")
        except ValueError:
            return None

    @classmethod
    def create_login_item(
        cls,
        *,
        account_uuid: str,
        vault_id: str,
        title: str,
        api_key: str,
        username: str | None = None,
        password: str | None = None,
        fqdn: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a 1Password Login item and return its op:// item reference.

        This method intentionally contains NO user interaction; callers should decide
        which vault/account to use (e.g., CLI prompts).

        The created item is compatible with TenantCredentialProviderFrom1Password:
        - api_key stored under field id/label 'api_key'
        - username/password stored under standard Login fields (purpose USERNAME/PASSWORD)
        - fqdn stored under 'fqdn' and optionally under urls[label=website] for discovery
        """

        item_template: dict = {
            "title": title,
            "category": "LOGIN",
            "fields": [
                {
                    "id": "api_key",
                    "label": "api_key",
                    "value": api_key,
                    "type": "CONCEALED",
                }
            ],
        }

        if tags:
            item_template["tags"] = tags

        if username:
            item_template["fields"].append(
                {
                    "id": "username",
                    "label": "username",
                    "value": username,
                    "type": "STRING",
                    "purpose": "USERNAME",
                }
            )

        if password:
            item_template["fields"].append(
                {
                    "id": "password",
                    "label": "password",
                    "value": password,
                    "type": "CONCEALED",
                    "purpose": "PASSWORD",
                }
            )

        if fqdn:
            item_template["fields"].append(
                {
                    "id": "fqdn",
                    "label": "fqdn",
                    "value": fqdn,
                    "type": "STRING",
                }
            )

            # Also add a website URL for better compatibility with get_fqdn()
            website_url = f"https://{fqdn.replace('api.', 'app.')}"
            item_template["urls"] = [
                {"label": "website", "href": website_url, "primary": True}
            ]

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as temp_file:
                json.dump(item_template, temp_file, indent=2)
                temp_path = temp_file.name

            cmd = [
                "op",
                "item",
                "create",
                "--account",
                account_uuid,
                "--vault",
                vault_id,
                "--template",
                temp_path,
                "--format",
                "json",
            ]
            out = subprocess.run(cmd, capture_output=True, text=True)
            if out.returncode != 0:
                raise Exception(out.stderr.strip() or "op item create failed")

            item = json.loads(out.stdout.strip())
            item_id = item["id"]
            return f"op://{vault_id}@{account_uuid}/{item_id}"
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

    def get_fqdn(self) -> Optional[str]:
        """Get FQDN from tenant config file first, then fallback to 1Password item.

        Checks in order:
        1. 1Password 'fqdn' field (explicit FQDN)
        2. 1Password 'urls' field - list of URL objects, looks for 'website' label or primary URL
        3. Returns None if neither found (will use DEFAULT_FQDN)
        """
        # Import here to avoid circular dependency
        from bpkio_api.api import BroadpeakIoApi

        # check for explicit fqdn field
        try:
            fqdn = self._get_item_field("fqdn")
            if fqdn:
                return BroadpeakIoApi.normalise_fqdn(fqdn)
        except ValueError:
            pass

        # check for urls field (list of URL objects)
        try:
            item = self._get_item()
            urls = item.get("urls", [])

            if urls:
                # Look for URL with label='website' first, then primary=True
                website_url = None
                primary_url = None

                for url_obj in urls:
                    if isinstance(url_obj, dict):
                        label = url_obj.get("label", "").lower()
                        href = url_obj.get("href")
                        is_primary = url_obj.get("primary", False)
                        is_bkpio = "broadpeak.io" in href or "ridgeline.fr" in href

                        if label == "website" and href and is_bkpio:
                            website_url = href
                            break  # Found the preferred website URL, stop loop
                        elif is_primary and href and not primary_url:
                            primary_url = href
                            break  # Found a primary URL, stop loop

                # Prefer website label, fall back to primary
                selected_url = website_url or primary_url
                if selected_url:
                    return BroadpeakIoApi.normalise_fqdn(selected_url)
        except (ValueError, KeyError, AttributeError):
            pass

        return None

    @staticmethod
    def extract_fqdn(item: dict) -> Optional[str]:
        return TenantCredentialProviderFrom1Password(item=item).get_fqdn()

    @functools.lru_cache(maxsize=10)
    def _get_item(self):
        if not self.item:
            op_credential = subprocess.run(
                [
                    "op",
                    "item",
                    "get",
                    self.item_id,
                    *(["--account", self.account_uuid] if self.account_uuid else []),
                    "--vault",
                    self.vault_name,
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if op_credential.returncode != 0:
                raise Exception(op_credential.stderr)

            response = op_credential.stdout.strip()
            self.item = json.loads(response)

        return self.item

    def _get_item_field(self, field_name: str):
        item = self._get_item()
        fields = item.get("fields", [])

        for field in fields:
            if field.get("id") == field_name:
                return field.get("value")
            if field.get("label") == field_name:
                return field.get("value")

        raise ValueError(
            f"Field `{field_name}` not found in 1Password item `{item.get('title')}`"
        )

    def _get_op_path(self, op_path: str, key: str):
        op_path = op_path.strip('"')
        op_full_path = f"{op_path}/{key}"
        op_credential = subprocess.run(
            ["op", "read", op_full_path], capture_output=True, text=True
        )
        return op_credential.stdout.strip()

    def store_info(self, info: dict) -> dict:
        stored_fields = ["api_key", "username", "password"]

        item = self._get_item()

        for key, value in info.items():
            if key not in stored_fields:
                continue

            found = False
            for field in item["fields"]:
                if field["id"] == key:
                    field["value"] = value
                    found = True
                    break
                elif field["label"] == key:
                    field["value"] = value
                    found = True
                    break
            if not found:
                # Ensure standard Login fields are created properly when missing.
                # Without purpose, 1Password treats username/password as custom fields.
                if key == "username":
                    new_custom_field = {
                        "id": "username",
                        "label": "username",
                        "value": value,
                        "type": "STRING",
                        "purpose": "USERNAME",
                    }
                elif key == "password":
                    new_custom_field = {
                        "id": "password",
                        "label": "password",
                        "value": value,
                        "type": "CONCEALED",
                        "purpose": "PASSWORD",
                    }
                else:
                    new_custom_field = {
                        "id": key,
                        "label": key,
                        "value": value,
                        "type": "CONCEALED",
                    }
                item["fields"].append(new_custom_field)

        # Save as a temporary JSON file
        temp_file = f"/tmp/{self.item_id}.json"
        with open(temp_file, "w") as f:
            json.dump(item, f)

        op_credential = subprocess.run(
            [
                "op",
                "item",
                "edit",
                self.item_id,
                *(["--account", self.account_uuid] if self.account_uuid else []),
                "--vault",
                self.vault_name,
                "--template",
                temp_file,
            ],
            capture_output=True,
            text=True,
        )
        logger.debug(op_credential.stdout)

        if op_credential.returncode != 0:
            raise Exception(op_credential.stderr)

        # Remove the temporary JSON file
        os.remove(temp_file)

        # remove the keys from the info dict
        for key in stored_fields:
            if key in info:
                info.pop(key)

        return info


@dataclass
class TenantProfile:
    label: str
    id: int
    fqdn: Optional[str] = DEFAULT_FQDN

    provider: Optional[TenantCredentialProvider] = None

    @property
    def username(self):
        return self.provider.get_username()

    @property
    def password(self):
        return self.provider.get_password()

    @property
    def api_key(self):
        return self.provider.get_api_key()

    @property
    def credential_source(self):
        return self.provider.source


class TenantProfileProvider:
    config = configparser.ConfigParser(interpolation=None)

    def __init__(self, filename: Optional[str] = None) -> None:
        f = Path(filename or DEFAULT_INI_FILE)
        if not f.exists():
            f.parent.mkdir(exist_ok=True, parents=True)
            f.touch()

        self._filename = f
        self._read_ini_file()

    @property
    def inifile(self):
        return self._filename

    def get_tenant_profile(self, tenant_label: str, resolve: bool = False):
        tenant_info = self._get_tenant_section(tenant_label)

        provider = tenant_info.get("provider")
        if not provider:
            credential_provider = TenantCredentialProviderFromConfigFile(
                tenant_info=tenant_info
            )
        elif provider.startswith(("op://", '"op://')):
            credential_provider = TenantCredentialProviderFrom1Password(
                item_ref=provider, tenant_info=tenant_info
            )
        else:
            raise NotImplementedError(f"Unsupported credential provider: {provider}")

        # Determine FQDN: use provider's FQDN (which handles config file and 1Password), fallback to default
        if resolve:
            logger.debug(f"Resolving FQDN and tenant ID for tenant `{tenant_label}`")
            fqdn, tenant_id = TenantCredentialProviderFrom1Password.extract_fqdn(
                credential_provider._get_item()
            )
        else:
            fqdn = tenant_info.get("fqdn") or DEFAULT_FQDN
            tenant_id = tenant_info.getint("id")

        tp = TenantProfile(
            label=tenant_label,
            id=tenant_id,
            fqdn=fqdn,
            provider=credential_provider,
        )
        return tp

    def list_tenants(self, resolve: bool = False):
        tenants = []
        for section in self.config.sections():
            tenants.append(self.get_tenant_profile(section, resolve=resolve))

        return tenants

    def has_tenant_label(self, tenant: str, fuzzy: bool = False):
        return tenant in self.config

    def find_matching_tenant_labels(self, tenant: str):
        candidates = []
        for section in self.config.sections():
            if tenant in section:
                candidates.append(section)

        return candidates

    def has_default_tenant(self):
        return self.has_tenant_label("default")

    # --- Core methods to read and write the `tenants` file ---

    def get_tenant_label_from_working_directory(self):
        try:
            with open(".tenant") as f:
                return f.read().strip()
        except Exception:
            return None

    def store_tenant_label_in_working_directory(self, tenant: str):
        with open(".tenant", "w") as f:
            f.write(tenant)

    def _get_tenant_section(self, tenant_label: str | None):
        tenant_section = None
        if tenant_label:
            if tenant_label in self.config:
                # tenant is the key in a section of the config file
                tenant_section = self.config[tenant_label]

            elif tenant_label.isdigit():
                # by tenant ID, in the first section that contains it
                for section in self.config.sections():
                    if (
                        "id" in self.config[section]
                        and self.config[section]["id"] == tenant_label
                    ):
                        tenant_section = self.config[section]

            if not tenant_section:
                raise NoTenantSectionError(
                    f"There is no tenant `{tenant_label}` in the file at {self._filename}"
                )

        if not tenant_section and "default" in self.config:
            # default section
            tenant_section = self.config["default"]

        if not tenant_section:
            raise NoTenantSectionError()

        # # Treat external credential providers
        # if tenant_section.get("api_key").strip('"').startswith("op://"):
        #     tenant_section['api_key'] = self._resolve_1password_credential(tenant_section.get("api_key"))
        #     tenant_section['_cred_source'] = "1Password"
        #     logger.debug(f"Resolved OP credential for tenant `{tenant}`")

        return tenant_section

    def _read_ini_file(self):
        # TODO - warning if the file does not exist
        self.config.read(DEFAULT_INI_FILE)

    def _from_config_file_section(self, tenant: str, key: str) -> str:
        return self.config[tenant][key]

    def _from_env(self, var) -> Optional[str]:
        return environ.get(var)

    def add_tenant(self, key: str, entries: dict):
        self.config[key] = entries
        with open(self._filename, "w") as ini:
            self.config.write(ini)

    def update_tenant(self, tenant_label: str, entries: dict):
        tenant = self.get_tenant_profile(tenant_label)
        remaining_entries = tenant.provider.store_credentials(entries)
        for key, value in remaining_entries.items():
            self.config[tenant_label][key] = value

        with open(self._filename, "w") as ini:
            self.config.write(ini)

    def remove_tenant(self, key: str):
        self.config.remove_section(key)
        with open(self._filename, "w") as ini:
            self.config.write(ini)

    @staticmethod
    def resolve_platform(platform):
        if platform == "prod":
            return "api.broadpeak.io"
        if platform == "staging":
            return "apidev.ridgeline.fr"
        return platform


class InvalidTenantError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NoTenantSectionError(Exception):
    def __init__(
        self,
        message: str = "No valid tenant section could be found in the tenant config file",
    ) -> None:
        super().__init__(message)
