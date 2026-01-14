import click
import cloup

from bpkio_cli.core.logging import logger
from bpkio_cli.core.plugin_manager import plugin_manager

PLUGIN_SECTION_NAME = "Plugin commands"
ADMIN_PLUGIN_SECTION_NAME = "🔒 Admin commands"

WantsPluginManager = click.make_pass_decorator(plugin_manager)


class AcceptsPluginsGroup(cloup.Group):
    def __init__(self, *args, **kwargs):
        self.plugin_manager = plugin_manager
        self.plugins = {}
        self.plugin_section = cloup.Section(PLUGIN_SECTION_NAME, is_sorted=True)
        self.admin_plugin_section = cloup.Section(
            ADMIN_PLUGIN_SECTION_NAME, is_sorted=True
        )
        self.plugins_discovered = False
        super().__init__(*args, **kwargs)

    def _fully_qualified_command_name(self, ctx):
        """Generate an optionally composite command name
        by traversing the chain of commands to the current one
        """
        cmd = ctx.command.name
        if hasattr(ctx, "parent") and ctx.parent is not None:
            if ctx.parent.command.name != "bic":
                cmd = self._fully_qualified_command_name(ctx.parent) + "." + cmd
        return cmd

    def discover_plugins(self, ctx):
        if self.plugins_discovered:
            return

        if ctx.params.get("safe") is True:
            logger.debug("Safe mode enabled, skipping plugin discovery")
            self.plugins_discovered = True
            return

        plugin_commands = self.plugin_manager.discover_commands()

        for plugin in plugin_commands:
            if hasattr(plugin, "scopes"):
                if not plugin.scopes or plugin.scopes == ["*"]:
                    # No specific scope, add to the current group
                    self._add_plugin_command(plugin)
                    continue

                if self._fully_qualified_command_name(ctx) in plugin.scopes:
                    self._add_plugin_command(plugin)

            else:
                # If no 'scopes' attribute, it's a general plugin for the top-level
                self._add_plugin_command(plugin)

        self.plugins_discovered = True

    def _add_plugin_command(self, plugin: click.Command):
        plugin_name = plugin.name
        if plugin_name in self.plugins:
            logger.warning(
                f"Duplicate plugin command '{plugin_name}' found. Overwriting."
            )

        self.plugins[plugin_name] = plugin
        try:
            logger.debug(f"Adding plugin '{plugin_name}' to group '{self.name}'")
            section = (
                self.admin_plugin_section
                if getattr(plugin, "admin_only", False)
                else self.plugin_section
            )
            self.add_command(plugin, plugin.name, section=section)
        except Exception as e:
            logger.error(f"Failed to add plugin command '{plugin_name}': {e}")

    def get_command(self, ctx, name):
        # Fast-path: if the command already exists (core command), don't pay plugin discovery.
        cmd = super().get_command(ctx, name)
        if cmd is not None:
            return cmd

        # Only discover plugins if the name isn't a known core command.
        self.discover_plugins(ctx)
        return super().get_command(ctx, name)

    def list_sections(self, ctx):
        # IMPORTANT: do not auto-discover plugins here.
        # cloup may call `list_sections()` during normal command resolution and we
        # don't want that to trigger importing every plugin (slow startup).
        #
        # Plugin commands will still be discovered on-demand via `get_command()`
        # when the user actually invokes an unknown command name.
        return super().list_sections(ctx)
