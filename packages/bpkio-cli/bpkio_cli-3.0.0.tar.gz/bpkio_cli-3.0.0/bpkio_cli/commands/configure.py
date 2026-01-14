import click
import cloup

import bpkio_cli.click_options as bic_options
from bpkio_cli.click_mods.accepts_plugins_group import AcceptsPluginsGroup
from bpkio_cli.click_mods.option_eat_all import OptionEatAll
from bpkio_cli.commands.tenant_profiles import add, tenants
from bpkio_cli.core.config_provider import CONFIG
from bpkio_cli.core.response_handler import ResponseHandler
from bpkio_cli.writers.players import StreamPlayer


# Command: INIT
# To be attached to the root group
@cloup.command(help="Initialize the tool, and create a first tenant profile")
@click.pass_context
def init(ctx):
    if not ctx.obj.tenant_provider.has_default_tenant():
        ctx.invoke(add)

    click.secho("All done!  You're ready to go now", fg="yellow")


# Group: CONFIG
@cloup.group(
    aliases=["config", "cfg"],
    help="Configure how the CLI works",
    show_subcommand_aliases=True,
    cls=AcceptsPluginsGroup,
)  # type: ignore
@click.pass_obj
def configure(obj):
    pass


# Command: SET
@configure.command(help="Set a configuration option")
@click.argument("key", required=True)
@click.argument("value", required=True)
def set(key, value):
    if "." in key:
        key_parts = key.split(".")
        section = key_parts[0]
        key = ".".join(key_parts[1:])
        CONFIG.set_config(key, value, section=section)
    else:
        CONFIG.set_config(key, value)


# Command: EDIT
@configure.command(help="Edit the config file")
def edit():
    config_file = CONFIG.config_path
    click.edit(filename=str(config_file), editor=CONFIG.get("editor"))


# =========

# Sub-group: TENANTS
configure.add_command(tenants)

# =========


# Sub-Group: PLAYERS
@configure.group(
    help="Management of player configurations",
    aliases=["player", "pl"],
)
@click.pass_obj
def players(obj):
    pass


# Command: LIST
@players.command(help="List the players already configured", aliases=["ls"])
@bic_options.output_formats
@click.option(
    "-s",
    "--sort",
    "sort_fields",
    cls=OptionEatAll,
    type=tuple,
    help="List of fields used to sort the list. Append ':desc' to sort in descending order",
)
@click.option(
    "--labels",
    "labels_only",
    is_flag=True,
    type=bool,
    default=False,
    help="Return the labels only, 1 per line. This can be useful for piping to other tools",
)
def list(sort_fields, labels_only, list_format):
    pl = StreamPlayer()
    ppl = pl.available_player_templates()
    if labels_only:
        ppl = [p for p in ppl.keys()]
        click.echo("\n".join(ppl))
    else:
        ppl = [v for k, v in ppl.items()]
        ResponseHandler().treat_list_resources(
            resources=ppl,
            # select_fields=["label", "id", "fqdn"],
            sort_fields=sort_fields,
            format=list_format,
        )


# =========


# Sub-Group: TEST
@configure.group(
    help="Test various configuration settings",
    aliases=["t"],
)
@click.pass_obj
def test(obj):
    pass


# Command: AUDIO
@test.command(help="Test audio notifications")
def audio():
    import os

    import bpkio_cli.utils.sounds as sounds
    from bpkio_cli.writers.colorizer import Colorizer as CL

    # Get configuration values
    audio_notifications = CONFIG.get("audio-notifications", cast_type=bool)
    bpkio_no_sound = os.environ.get("BIC_NO_SOUND", "")

    # Detect audio mechanism
    mechanism = sounds.detect_audio_mechanism()

    # Display status
    click.echo("\nAudio Configuration Status:")
    click.echo("─" * 50)

    # Config setting
    config_status = CL.ok("enabled") if audio_notifications else CL.warning("disabled")
    click.echo(f"  audio-notifications: {config_status}")

    # Environment variable
    if bpkio_no_sound:
        env_status = CL.warning(f"set to '{bpkio_no_sound}' (disables audio)")
    else:
        env_status = CL.ok("not set")
    click.echo(f"  BIC_NO_SOUND:      {env_status}")

    # Audio mechanism
    click.echo(f"  Audio mechanism:     {mechanism}")

    click.echo("─" * 50)

    # Check if audio will actually play
    bpkio_no_sound_lower = bpkio_no_sound.strip().lower()
    will_play = audio_notifications and bpkio_no_sound_lower not in {
        "1",
        "true",
        "yes",
        "on",
    }

    if will_play:
        click.echo("\nPlaying test sound (chime_uphigh)...")
        sounds.chime_uphigh()
        click.echo(CL.ok("Sound triggered!"))
    else:
        click.echo("\n" + CL.warning("Audio is disabled, so no sound will play."))
        if not audio_notifications:
            click.echo("  → Enable with: bic config set audio-notifications true")
        if bpkio_no_sound:
            click.echo("  → Unset BIC_NO_SOUND environment variable to enable")


# =========
