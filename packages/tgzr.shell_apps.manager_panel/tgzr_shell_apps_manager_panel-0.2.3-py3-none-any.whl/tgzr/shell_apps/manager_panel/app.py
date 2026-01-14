from pathlib import Path

import click
import pydantic

from tgzr.cli.utils import TGZRCliGroup
from tgzr.shell.app_sdk.nice_app import ShellNiceApp, ShellAppSettings

from . import run_native, run_dev
from . import pages


class SettingsTabSettings(pydantic.BaseModel):
    auto_expand_groups: bool = True


class ManagerPanelSettings(ShellAppSettings):
    settings_tab: SettingsTabSettings = pydantic.Field(
        default_factory=SettingsTabSettings
    )
    show_session_tab: bool = True
    show_install_tab: bool = False
    show_dev_tab: bool = False


class ManagerPanelApp[SettingsType: ShellAppSettings](ShellNiceApp[SettingsType]):
    # SETTTINGS_MODEL = ManagerPanelSettings

    def cli_run_cmd_installed(
        self, created_cmd: click.Command, root_group: TGZRCliGroup
    ):
        """
        Called when tgzr.shell.cli_plugin.app_cli has created and
        registered a cli command to execute this app.

        Overridden to set our command as default command if no higher
        order default command was set.
        """
        # If the cli's default command was set by tgzr.cli or tgzr.shell,
        # we want to override it with our own command:
        cmd, kwargs, setter = root_group.get_default_command()
        if setter and (
            setter.startswith("tgzr.cli") or setter.startswith("tgzr.shell")
        ):
            # print("tgzr.shell_app.manager_panel uninstalling default cmd from", setter)
            root_group.set_default_command(created_cmd)
            # cmd, kwargs, setter = root_group.get_default_command()
            # print("  new setter:", setter)


app = ManagerPanelApp[ManagerPanelSettings](
    "manager",
    run_native_module=run_native,
    run_dev_module=run_dev,
    static_file_path=Path(pages.__file__).parent / "static_files",
    app_groups={"Manage"},
    default_settings=ManagerPanelSettings(),
)
