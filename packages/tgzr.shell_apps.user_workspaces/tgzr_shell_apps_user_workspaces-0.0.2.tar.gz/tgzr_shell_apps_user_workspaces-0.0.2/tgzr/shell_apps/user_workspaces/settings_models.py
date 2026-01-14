import pydantic

from tgzr.shell.app_sdk.nice_app import ShellAppSettings
from tgzr.contextual_settings.items import Collection, NamedItem


class UserWorkspacesSettings(ShellAppSettings):
    workspace_names: list[str] = []
    default_workspace: str | None = None
    some_setting: str | None = None
    open_node_on_select: bool = False
    open_node_on_hover: bool = False
    show_lib_packages: bool = False


class Repo(NamedItem):
    path: str = ""


class UserWorkspaceWorkspaceSettings(pydantic.BaseModel):
    repos: Collection[Repo] = Collection[Repo].Field(Repo)
    default_repo: str | None = None
    blessed_repo: str | None = None
