import os
import sys
from typing import Optional

import click
from bpkio_api import BroadpeakIoApi
from bpkio_api.credential_provider import TenantProfileProvider
from bpkio_api.endpoints.login import LoginApi
from bpkio_api.exceptions import (
    AccessForbiddenError,
    ExpiredApiKeyFormat,
    InvalidApiKeyFormat,
    InvalidTenantError,
    MissingApiKeyError,
    NoTenantSectionError,
    PasswordExpiredError,
    UnauthorizedError,
)
from bpkio_api.models import BaseResource
from bpkio_cli import __version__ as CLI_VERSION
from bpkio_cli.core.app_context import AppContext
from bpkio_cli.core.config_provider import CONFIG
from bpkio_cli.core.exceptions import BroadpeakIoCliError
from bpkio_cli.core.plugin_manager import plugin_manager
from bpkio_cli.writers.breadcrumbs import (
    display_error,
    display_ok,
    display_tip,
    display_warning,
)
from loguru import logger

cli_agent = f"bpkio-cli/{CLI_VERSION}"


def initialize(
    requires_api: bool,
    tenant_ref: str | int | None = None,
    use_cache: bool = True,
    *,
    enable_media_muncher: bool = False,
) -> AppContext:
    """Function that initialises the CLI

    If a tenant label or ID is provided, the CLI will be initialised for that tenant.
    Otherwise, the CLI will be initialised with the last tenant used (and stored in
    a `.tenant` file).

    Successful initialisation requires that there is a profile in ~/.bpkio/tenants
    for that tenant.

    Args:
        tenant_ref (str | int): Name of the CLI profile
        use_cache (bool): Whether to use the cache

    Raises:
        click.Abort: if no tenant profile could be found in the ~/.bpkio/tenants file

    Returns:
        AppContext: The config for the app
    """
    tp = TenantProfileProvider()

    # Track whether tenant_ref came from .tenant file
    tenant_from_file = False

    # No specific tenant provided, see if there is one defined for the current directory
    if not tenant_ref:
        tenant_ref = tp.get_tenant_label_from_working_directory()
        if tenant_ref:
            tenant_from_file = True
    else:
        tenant_ref = str(tenant_ref)

    # Validate the tenant reference with fuzzy search (if not a numeric ID)
    if tenant_ref and not tenant_ref.isdigit():
        if not tp.has_tenant_label(tenant_ref):
            candidates = tp.find_matching_tenant_labels(tenant_ref)
            if len(candidates) == 1:
                tenant_ref = candidates[0]
            elif len(candidates) == 0:
                # No matching tenants found at all
                error_msg = f"No tenant profile found matching '{tenant_ref}'."

                # If tenant came from .tenant file, offer to delete it
                if tenant_from_file and os.path.exists(".tenant"):
                    display_warning(
                        f"The tenant '{tenant_ref}' was read from the local '.tenant' file, "
                        "but no matching tenant profile exists."
                    )
                    from bpkio_cli.utils import prompt

                    if prompt.confirm(
                        "Do you want to delete the '.tenant' file?", default=True
                    ):
                        try:
                            os.remove(".tenant")
                            display_ok("Deleted '.tenant' file.")
                            display_tip(
                                "You can set a tenant for this folder with `bic config tenant switch`, or use the `--tenant` flag in your next command"
                            )
                        except Exception as e:
                            display_error(f"Failed to delete '.tenant' file: {e}")

                raise BroadpeakIoCliError(error_msg)
            else:
                display_warning("No tenant profile found for the provided label. ")
                from bpkio_cli.utils import prompt

                tenant_ref = prompt.fuzzy(
                    message="Did you mean?",
                    choices=candidates,
                )

    # Define a file to store a recording of actions
    from bpkio_cli.core.session_recorder import get_session_file

    session_file = get_session_file()

    # Ensure media_muncher uses the same SSL verification settings as the CLI.
    #
    # This is important when working behind corporate TLS-intercepting proxies
    # (custom CA bundle): many commands use media_muncher indirectly (e.g. source
    # compatibility checks), not just `bic url` / `bic archive`.
    #
    # Import ONLY the lightweight generic handler (do NOT import `media_muncher.handlers`,
    # which pulls heavy optional deps like dash/plotly).
    try:
        from media_muncher.handlers.generic import ContentHandler

        # Append to the content handler client string (sent as header)
        ContentHandler.api_client = cli_agent + " " + ContentHandler.api_client

        # Set verify_ssl for the content handlers as well (bool or path to CA bundle)
        ContentHandler.verify_ssl = CONFIG.get("verify-ssl", "bool_or_str")
    except Exception:
        # media_muncher is optional in some environments; ignore if unavailable.
        pass

    try:
        api = BroadpeakIoApi(
            tenant=tenant_ref,
            use_cache=use_cache,
            session_file=session_file,
            user_agent=cli_agent,
            verify_ssl=CONFIG.get("verify-ssl", "bool_or_str"),
            api_client=f"bpkio-cli/{CLI_VERSION}",
        )
        app_context = AppContext(api=api, tenant_provider=TenantProfileProvider())

        if CONFIG.get("verbose", int) > 0:
            full_tenant = api.get_self_tenant()
            app_context.tenant = full_tenant
        else:
            app_context.tenant = BaseResource(id=api.get_tenant_id())

        # Check size of the session recorder, in case it was left on
        # from a previous run.
        if api.session_recorder.is_active():
            click.secho(
                "⚠️  WARNING: Active recording session (with %s records)"
                % api.session_recorder.size(),
                fg="magenta",
                err=True,
            )

        return app_context

    except NoTenantSectionError as e:
        if requires_api:
            raise BroadpeakIoCliError(
                f"This command requires a valid tenant to be specified: {e}"
            )

    except InvalidTenantError:
        if requires_api:
            raise BroadpeakIoCliError(
                "This command requires a valid tenant to be configured. Try `bic init` to configure a tenant."
            )

    except (
        AccessForbiddenError,
        InvalidApiKeyFormat,
        ExpiredApiKeyFormat,
        MissingApiKeyError,
    ) as e:
        if requires_api:
            display_error(f"Error initializing the API for tenant `{tenant_ref}`: {e}.")

            # Try automatic login fallback
            new_api_key = attempt_auto_login(tenant_ref)

            if new_api_key:
                # Retry with new token
                try:
                    api = BroadpeakIoApi(
                        tenant=tenant_ref,
                        use_cache=use_cache,
                        session_file=session_file,
                        user_agent=cli_agent,
                        verify_ssl=CONFIG.get("verify-ssl", "bool_or_str"),
                        api_client=f"bpkio-cli/{CLI_VERSION}",
                    )
                    app_context = AppContext(
                        api=api, tenant_provider=TenantProfileProvider()
                    )

                    if CONFIG.get("verbose", int) > 0:
                        full_tenant = api.get_self_tenant()
                        app_context.tenant = full_tenant
                    else:
                        app_context.tenant = BaseResource(id=api.get_tenant_id())

                    display_tip("Successfully authenticated and retrying command...")
                    return app_context
                except Exception as retry_error:
                    display_error(f"Retry failed after auto-login: {retry_error}")
                    raise click.Abort()

            # If auto-login didn't work, provide manual instructions
            handle_missing_or_invalid_api_key(tenant_ref, attempted_auto_login=True)
            raise click.Abort()

    except Exception as e:
        if requires_api:
            raise BroadpeakIoCliError(f"Error initialising the CLI: {e}")

    return AppContext(
        api=None,
        tenant_provider=TenantProfileProvider(),
    )


def attempt_auto_login(tenant_ref: str) -> Optional[str]:
    """Attempt to login with username/password and update stored credentials.

    Returns:
        The new API key if successful, None otherwise
    """
    tp = TenantProfileProvider()

    try:
        tenant_profile = tp.get_tenant_profile(tenant_ref)
    except Exception as e:
        logger.debug(f"Could not get tenant profile: {e}")
        return None

    username = tenant_profile.username
    password = tenant_profile.password

    if not username or not password:
        display_warning("No username/password configured - cannot auto-login")
        return None

    if CONFIG.get("verbose", int) > 0:
        display_tip(f"Attempting automatic login for {username}...")

    try:
        # Use FQDN from tenant profile (may come from 1Password website field, config file, or default)
        base_url = f"https://{tenant_profile.fqdn}/v1/"
        login_api = LoginApi(
            base_url, auth=None, verify_ssl=CONFIG.get("verify-ssl", "bool_or_str")
        )
        response = login_api.login_with_credentials(email=username, password=password)

        new_api_key = response.token

        # Update the stored credentials
        tp.update_tenant(tenant_profile.label, {"api_key": new_api_key})

        expiration_str = (
            response.expirationDate.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(response.expirationDate, "strftime")
            else str(response.expirationDate)
        )
        display_ok(f"Login successful! API key updated (expires: {expiration_str})")

        # Suggest webapp automation for longer-lived keys
        create_apikey_in_webapp = plugin_manager.get_service(
            "create_apikey_in_webapp", optional=True
        )
        if create_apikey_in_webapp:
            display_tip(
                f"For a longer-lived API key, run: bic config tenant {tenant_profile.label} apikey create"
            )

        return new_api_key

    except PasswordExpiredError:
        display_error(
            "Your password has expired. Please update your password in the webapp."
        )
        raise click.Abort()

    except UnauthorizedError as e:
        display_error(f"Login failed: {e.message}")
        return None

    except Exception as e:
        display_error(f"Auto-login failed: {e}")
        return None


def handle_missing_or_invalid_api_key(
    tenant_ref: str, attempted_auto_login: bool = False
):
    """Fallback when auto-login is not available or failed.

    Args:
        tenant_ref: The tenant label
        attempted_auto_login: Whether auto-login was already attempted (for messaging)
    """
    tenant_info = TenantProfileProvider().get_tenant_profile(tenant_ref)

    # Try auto-login first if we haven't already attempted it and credentials are available
    if not attempted_auto_login:
        new_api_key = attempt_auto_login(tenant_ref)
        if new_api_key:
            display_tip("API key updated successfully. Please try the command again.")
            return

    # Only offer webapp automation if we have username
    create_apikey_in_webapp = plugin_manager.get_service(
        "create_apikey_in_webapp", optional=True
    )
    if create_apikey_in_webapp and tenant_info.username:
        message = (
            "Auto-login failed. Do you want to create a new API key via webapp?"
            if attempted_auto_login
            else "Do you want to create a new API key via webapp?"
        )
        from bpkio_cli.utils import prompt

        do_create = prompt.confirm(
            message,
            default=True,
        )

        if do_create:
            create_apikey_in_webapp(
                tenant_info,
                TenantProfileProvider(),
                headless=True,
            )

            display_tip("API key created successfully. Please try the command again.")
            sys.exit(1)

    display_tip(
        f"Please create a new API key in the webapp and update your tenant profile "
        f"(`bic config tenant {tenant_ref} apikey change`)."
    )
