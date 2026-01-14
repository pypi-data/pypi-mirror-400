from __future__ import annotations

from pathlib import Path

import rich
import click
import pydantic

from tgzr.cli.utils import TGZRCliGroup
from tgzr.shell.app_sdk.nice_app import ShellNiceApp, ShellAppSettings, NiceAppState
from tgzr.pipeline.workspace import WorkspaceSettings

from . import run_native, run_dev
from . import pages
from .settings_models import UserWorkspacesSettings


class UserWorkspaceAppState[AppSettingsType: UserWorkspacesSettings](
    NiceAppState[AppSettingsType]
):
    _current_workspace_settings_cache: WorkspaceSettings | None = None

    @classmethod
    def from_nice_state(cls, nice_app_state: NiceAppState):
        return cls(
            visid=nice_app_state.visid,
            session=nice_app_state.session,
            _app=nice_app_state.app,
            data=nice_app_state.data,
        )

    def get_workspace_names(self) -> list[str]:
        settings = self.app_settings()
        return settings.workspace_names

    @property
    def workspace_name(self) -> str | None:
        return self._current_workspace

    @workspace_name.setter
    def workspace_name(self, workspace_name: str | None):
        self._current_workspace = workspace_name
        self._current_workspace_settings_cache = None

    @property
    def workspace_settings_key(self) -> str:
        return self.app.settings_key + f".workspaces.{self.workspace_name}"

    @property
    def workspace_settings_context(self) -> list[str]:
        return [
            *self.session.context.settings_base_context,
            *self.settings_session_context,
            *(self.workspace_name and [self.workspace_name] or []),
        ]

    def workspace_settings(self, reload: bool = False) -> WorkspaceSettings:
        if reload or self._current_workspace_settings_cache is None:
            settings = self.session.settings.get_context(
                self.workspace_settings_context,
                WorkspaceSettings,
                self.workspace_settings_key,
            )
            self._current_workspace_settings_cache = settings
        return self._current_workspace_settings_cache


class UserWorkspaceApp[SettingsType: UserWorkspacesSettings](
    ShellNiceApp[SettingsType]
):

    def create_app_state(self) -> UserWorkspaceAppState[SettingsType]:
        nice_state = super().create_app_state()
        user_workspace_app_state = UserWorkspaceAppState.from_nice_state(nice_state)
        return user_workspace_app_state

    def cli_run_cmd_installed(
        self, created_cmd: click.Command, root_group: TGZRCliGroup
    ):
        pass  # this is for later...
        # """
        # Called when tgzr.shell.cli_plugin.app_cli has created and
        # registered a cli command to execute this app.

        # Overridden to set our command as default command if no higher
        # order default command was set.
        # """
        # # If the cli's default command was set by tgzr.cli or tgzr.shell,
        # # we want to override it with our own command:
        # cmd, kwargs, setter = root_group.get_default_command()
        # if setter and (
        #     setter.startswith("tgzr.cli") or setter.startswith("tgzr.shell")
        # ):
        #     # print("tgzr.shell_app.manager_panel uninstalling default cmd from", setter)
        #     root_group.set_default_command(created_cmd)
        #     # cmd, kwargs, setter = root_group.get_default_command()
        #     # print("  new setter:", setter)


app = UserWorkspaceApp[UserWorkspacesSettings](
    "user_workspaces",
    run_native_module=run_native,
    run_dev_module=run_dev,
    static_file_path=Path(pages.__file__).parent / "static_files",
    app_groups={"Manage"},
    default_settings=UserWorkspacesSettings(),
)
