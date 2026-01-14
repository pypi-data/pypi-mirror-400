import json
import subprocess

from bpkio_api.defaults import DEFAULT_FQDN
from bpkio_api.credential_provider import TenantCredentialProviderFrom1Password
from loguru import logger

from bpkio_cli.utils import prompt
from bpkio_cli.writers.breadcrumbs import display_error, display_ok


def is_op_secret(secret: str):
    return secret.strip().strip('"').startswith("op://")


def get_accounts():
    output = subprocess.run(
        ["op", "account", "list", "--format", "json"], capture_output=True, text=True
    )
    return json.loads(output.stdout.strip())


def get_op_vaults(account: dict):
    output = subprocess.run(
        [
            "op",
            "vault",
            "list",
            "--format",
            "json",
            "--account",
            account["account_uuid"],
        ],
        capture_output=True,
        text=True,
    )
    return json.loads(output.stdout.strip())


def get_all_op_vaults():
    accounts = get_accounts()
    all_vaults = []
    for account in accounts:
        vaults = get_op_vaults(account)
        for v in vaults:
            v["account_email"] = account["email"]
            v["account_uuid"] = account["account_uuid"]
            v["account_url"] = account["url"]
            v["vault_label"] = v["name"]
            if len(accounts) > 1:
                v["vault_label"] = f"[{v['account_url']}] {v['vault_label']}"
            all_vaults.append(v)
    return all_vaults


def list_all_candidate_items():
    all_vaults = get_all_op_vaults()
    vault = prompt.fuzzy(
        message="Select a vault",
        choices=[prompt.Choice(name=v["vault_label"], value=v) for v in all_vaults],
    )

    output = subprocess.run(
        [
            "op",
            "item",
            "list",
            "--vault",
            vault["id"],
            "--account",
            vault["account_uuid"],
            "--categories",
            "Login",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    j = json.loads(output.stdout.strip())
    for i in j:
        i["vault"]["account_uuid"] = vault["account_uuid"]

    return j


def get_detailed_item(item_id: str, account_uuid: str, vault_id: str):
    output = subprocess.run(
        [
            "op",
            "item",
            "get",
            item_id,
            "--account",
            account_uuid,
            "--vault",
            vault_id,
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    return json.loads(output.stdout.strip())


def store_tenant_credentials_in_op(
    api_key: str,
    tenant_label: str,
    fqdn: str,
    username: str = None,
    password: str = None,
):
    """Store tenant credentials in 1Password and return an op:// item reference.

    Vault/account selection is handled here (CLI prompt). The SDK performs the actual
    item creation with no user interaction.
    """
    all_vaults = get_all_op_vaults()

    # Prompt the user to select a vault
    vault = prompt.fuzzy(
        message="Select a vault",
        choices=[prompt.Choice(name=v["vault_label"], value=v) for v in all_vaults],
    )

    title = f"{tenant_label}"
    if "@" not in tenant_label:
        if fqdn == DEFAULT_FQDN:
            title += " @ prod"
        else:
            title += f" @ {fqdn.split('.')[0].replace('api', '')}"

    try:
        item_ref = TenantCredentialProviderFrom1Password.create_login_item(
            account_uuid=vault["account_uuid"],
            vault_id=vault["id"],
            title=title,
            api_key=api_key,
            username=username,
            password=password,
            fqdn=None if fqdn == DEFAULT_FQDN else fqdn,
            tags=["Added by broadpeak.io CLI"],
        )
    except Exception as e:
        display_error(f"Failed to store credentials in 1Password: {e}")
        return api_key

    display_ok(f"Tenant credentials stored in 1Password under name: {title}")
    return item_ref


def is_op_cli_installed():
    try:
        # Try running `op --version` to check if the CLI is installed
        result = subprocess.run(
            ["op", "--version"], capture_output=True, text=True, check=True
        )
        logger.debug(f"1Password CLI is installed. Version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        # `op` command not found
        logger.debug("1Password CLI is not installed.")
        return False
    except subprocess.CalledProcessError:
        # Command found, but failed for some other reason
        logger.debug("1Password CLI is installed but returned an error.")
        return True
    except Exception as e:
        logger.debug(f"Failed to check whether 1Password CLI was installed: {e}")
        return False
