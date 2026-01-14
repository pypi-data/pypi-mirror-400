from __future__ import annotations
from typing import TYPE_CHECKING, cast

import dataclasses
from importlib.metadata import Distribution
from packaging.requirements import Requirement
from keyword import iskeyword
import re
from types import SimpleNamespace

from nicegui.event import Event as NiceEvent
from nicegui import ui

from tgzr.pipeline.workspace import Workspace, DistInfo, AssetTypeInfo
from tgzr.shell.package_manager import Venv
from tgzr.nice.data_elements.dict_tree import (
    TreeGroup,
    TreeView,
    read_only_input_renderer,
)

from .utils import async_call_with_progress, message_dialog

if TYPE_CHECKING:
    from ..app import UserWorkspaceAppState, UserWorkspacesSettings

    StateType = UserWorkspaceAppState[UserWorkspacesSettings]


def _get_venv_packages(
    workspace_venv_path: str,
) -> list[Distribution]:
    venv = Venv(workspace_venv_path)
    return venv.get_packages()


def _get_venv_package(
    workspace_venv_path: str, package_name: str
) -> Distribution | None:
    venv = Venv(workspace_venv_path)
    return venv.get_package(package_name)


class PageState:

    @dataclasses.dataclass
    class Events:
        on_exception: NiceEvent[Exception] = dataclasses.field(
            default_factory=NiceEvent[Exception]
        )

        reload_request: NiceEvent = dataclasses.field(default_factory=NiceEvent)
        reload: NiceEvent = dataclasses.field(default_factory=NiceEvent)

        show_dist: NiceEvent[str] = dataclasses.field(default_factory=NiceEvent[str])
        shown_dists_changed: NiceEvent = dataclasses.field(default_factory=NiceEvent)
        show_dist_info: NiceEvent[str] = dataclasses.field(
            default_factory=NiceEvent[str]
        )

        # layout: NiceEvent = dataclasses.field(default_factory=NiceEvent)

        add_input: NiceEvent[str] = dataclasses.field(default_factory=NiceEvent[str])
        current_changed: NiceEvent[str] = dataclasses.field(
            default_factory=NiceEvent[str]
        )

        bump: NiceEvent[str] = dataclasses.field(default_factory=NiceEvent[str])
        execute_console_script: NiceEvent[str, str] = dataclasses.field(
            default_factory=NiceEvent[str, str]
        )

    def __init__(self, state: StateType, workspace: Workspace | None) -> None:
        self.state = state
        self._workspace = workspace

        self._asset_types_info = self.workspace.get_asset_types_info()
        self.events = self.Events()

        self._dists = None
        self._dist_by_name: dict[str, Distribution] = {}
        self._shown_dists: list[Distribution] = []

        self.show_multiple = True

        self.events.show_dist.subscribe(self.show_dist)
        self.events.show_dist_info.subscribe(self.show_dist_info)
        self.events.add_input.subscribe(self.add_input)

        self.events.bump.subscribe(self._on_bump_request)
        self.events.execute_console_script.subscribe(
            self._on_execute_console_script_request
        )

        self.events.reload.subscribe(self.clear_cache)

    @property
    def workspace(self) -> Workspace:
        try:
            assert self._workspace is not None
        except Exception as err:
            self.events.on_exception.emit(err)
            raise
        return self._workspace

    def asset_type_info(self, dist_info: DistInfo) -> AssetTypeInfo | None:
        if not dist_info.is_asset or dist_info.asset_type is None:
            return AssetTypeInfo(
                type_name="lib",
                category="lib",
                icon="sym_o_deployed_code",
                color="#737373",
            )

        try:
            ati = self._asset_types_info[dist_info.asset_type]
        except KeyError:
            return None
        return ati

    def asset_type_names(self) -> list[str]:
        return sorted(self._asset_types_info.keys())

    async def _load_venv_data(self):
        dists = cast(
            list[Distribution],
            await async_call_with_progress(
                _get_venv_packages, self.workspace.venv_path
            ),
        )
        return dists

    def clear_cache(self):
        self._dists = None

    async def ensure_loaded(self):
        await self.dists()

    def canonicalize_name(
        self,
        name: str,
    ) -> str:
        # Taken from pip :
        # https://github.com/pypa/pip/blob/1b4f3a49c1131b6863e069894d5c646b6803ce36/src/pip/_vendor/packaging/utils.py#L46
        _canonicalize_regex = re.compile(r"[-_.]+")
        # This is taken from PEP 503.
        value = _canonicalize_regex.sub("-", name).lower()
        return value

    async def dists(self) -> list[Distribution]:
        if self._dists is None:
            self._dists = await self._load_venv_data()
            canonicalize_name = self.canonicalize_name  # for speed
            self._dist_by_name = dict(
                [(canonicalize_name(d.name), d) for d in self._dists]
            )
            # rich.print(self._dist_by_name.keys())
        return self._dists

    async def has_dist(self, dist_name: str):
        await self.ensure_loaded()
        return dist_name in self._dist_by_name

    async def get_dist(
        self, dist_name: str, exception_notify: bool = True
    ) -> Distribution:
        await self.ensure_loaded()
        dist_name = self.canonicalize_name(dist_name)
        try:
            return self._dist_by_name[dist_name]
        except Exception as err:
            if exception_notify:
                self.events.on_exception.emit(err)
            raise

    async def get_required(
        self, dist: Distribution, extra: str | None = None
    ) -> list[Distribution]:
        required = []
        for requirement in dist.requires or []:
            req = Requirement(requirement)
            if 0:
                # TODO: Solidify this
                if extra is not None and extra not in req.extras:
                    print(
                        "!!!!!: skipping extra different than requested:",
                        dist.name,
                        "->",
                        req,
                    )
                    continue
                if extra is None and req.extras:
                    print(
                        "!!!!!: skipping extra when no extra was requested:",
                        dist.name,
                        "->",
                        req,
                    )
                    continue
            try:
                req_dist = await self.get_dist(req.name, exception_notify=False)
            except KeyError as err:
                if (
                    "platform_system" in str(req.marker)
                    or "sys_platform" in str(req.marker)
                    or "python_version" in str(req.marker)
                ):
                    # 1)
                    # When the requirement is for another platform, like:
                    #   colorama; platform_system == 'Windows'
                    # or
                    #   pywin32-ctypes>=0.2.0; sys_platform == "win32"
                    # and you're on Linux, the dist is not installed.
                    # Until we deal with platform specific requirement in pipeline
                    # we just silence this error...
                    # 2)
                    # When the requirement is for another python version, like:
                    #   python_version < "3.11"
                    # and you're on 3.12, the dist is not installed.
                    # We should be able to test if the dist is actually missing
                    # based on the workspace venv, but I don't think it's worse it.
                    continue
                if "extra ==" in str(req.marker):
                    # I'm not sure about this one, but until we use extra
                    # for asset dependencies I'll just print it out:
                    print(
                        f"!!!! Warning: Could not resolve requirement, maybe bc there is an extra: {req}"
                    )
                    continue
                # print("+++++++!!!", dist.name, "->", requirement)
                print("???? REQUIRED DIST NOT FOUND:", req)
                self.events.on_exception.emit(err)
                raise  # other unknown reasons must raise.
            else:
                required.append(req_dist)
        return required

    async def get_required_by(self, dist: Distribution) -> list[Distribution]:
        req_by = []
        dist_name = self.canonicalize_name(dist.name)
        for dist in await self.dists():
            for req in dist.requires or []:
                package = Requirement(req).name
                package = self.canonicalize_name(package)
                if package == dist_name:
                    req_by.append(dist)
        return req_by

    async def output_assets(self) -> list[DistInfo]:
        editables = []
        for dist in await self.dists():
            dist_info = self.workspace.get_dist_info(dist)
            if dist_info.is_editable:
                editables.append(dist_info)
        return editables

    async def show_dist(self, dist_name: str, x: int = 0, y: int = 0):
        dist = await self.get_dist(dist_name)
        if dist in self._shown_dists:
            return

        if not self.show_multiple:
            self._shown_dists.clear()
        self._shown_dists.append(dist)
        self.events.shown_dists_changed.emit()

    @property
    def shown_dists(self) -> tuple[Distribution, ...]:
        return tuple(self._shown_dists)

    async def _on_bump_request(self, dist_name: str):
        dist = await self.get_dist(dist_name)
        dist_info = self.workspace.get_dist_info(dist)
        data = SimpleNamespace(action=None)
        async for elem in message_dialog(button=None, big=False):
            with elem:
                ui.label(f"Bump Version for {dist_info.asset_name}").classes("text-h5")
                make_it_ediable_cb = None
                show_bumpers = True
                button_label = "Go"
                if not dist_info.is_editable:
                    ui.label(
                        f"You can´t modify the version of a package if it's not editable."
                    )
                    show_bumpers = False
                    if not dist_info.is_asset:
                        ui.label(
                            f"The package {dist_info.dist.name} is not an asset, "
                            "so you can't make it editable."
                        )
                        ui.label("You may install another version if you need.")
                    else:
                        make_it_ediable_cb = ui.checkbox(
                            "Make this asset Editable (not implemented)",
                        )
                with ui.column() as bump_group:
                    with ui.row():
                        major_cb = ui.checkbox("Major")
                        minor_cb = ui.checkbox("Minor")
                        micro_cb = ui.checkbox("Micro")
                    with ui.row():
                        alpha_cb = ui.checkbox("alpha")
                        beta_cb = ui.checkbox("beta")
                        preview_cb = ui.checkbox("preview")
                    with ui.row():
                        post_cb = ui.checkbox("post")
                        dev_cb = ui.checkbox("dev")
                    bump_group.set_visibility(show_bumpers)
                    if make_it_ediable_cb is not None:
                        make_it_ediable_cb.on_value_change(
                            lambda e: bump_group.set_visibility(e.value)
                        )

                def on_button():
                    data.action = "Go"
                    elem.dialog.close()  # type: ignore 🫣

                with ui.row().classes("w-full"):
                    ui.space()
                    ui.button(button_label, on_click=on_button)
        if data.action is None:
            return
        if make_it_ediable_cb is not None:
            if make_it_ediable_cb.value:
                ui.notify(
                    "Make it editable befor bump: Not implemented 🫣", position="top"
                )
            else:
                return
        print(
            "--> BUMPING",
            major_cb.value,
            minor_cb.value,
            micro_cb.value,
            alpha_cb.value,
            beta_cb.value,
            preview_cb.value,
            post_cb.value,
            dev_cb.value,
        )

    async def _on_execute_console_script_request(self, dist_name, console_script_name):
        # TODO: shouldn't we assert there's only one entry point for that script and it belongs to that dist?
        self.workspace.run(console_script_name)

    async def add_input(self, dist_name: str):
        def name_validation(value: str):
            if self.canonicalize_name(dist_name) in [
                i.strip() for i in value.split(" ")
            ]:
                return "!!! Cannot add itseld to its inputs!!!"

        with ui.dialog() as dialog, ui.card():
            requs_input = ui.input(
                label="Input (requirements)",
                placeholder="asset_name==1.2.3 tool_name>3.0",
                validation=name_validation,
            )
            with ui.row().classes("w-full"):
                ui.button(
                    f"Add input(s) to {dist_name}",
                    on_click=lambda: dialog.submit(requs_input.value),
                )

        reqs = await dialog
        if reqs is None:
            return
        requirements = [self.canonicalize_name(i).strip() for i in reqs.split()]
        try:
            self.workspace.add_inputs(dist_name, *requirements)
        except Exception as err:
            self.events.on_exception.emit(err)
            # ui.notify(err, type="negative", position="top")
        self.clear_cache()
        await self.ensure_loaded()

    async def show_dist_info(self, dist_name: str):
        dist = await self.get_dist(dist_name)
        dist_info = self.workspace.get_dist_info(dist)
        await self.dist_info_dialog(dist_info=dist_info)

    async def dist_info_dialog(self, dist_info: DistInfo):
        asset_info = dataclasses.asdict(dist_info)
        del asset_info["dist"]

        dist = dist_info.dist
        eps = {}
        for ep in dist.entry_points:
            group = eps.get(ep.group)
            if group is None:
                group = {}
                eps[ep.group] = group
            group[ep.name] = ep.value

        dist_details = dict(
            package_name=dist.name,
            cannonical_package_name=self.canonicalize_name(dist.name),
            requires=dist.requires,
            required_by=[d.name for d in await self.get_required_by(dist)],
            entry_points=eps,
            metadata=dist.metadata.json,
            origin=dist.origin and vars(dist.origin) or None,
        )
        info = dict(
            path="/path/to/asset",
            asset=asset_info,
            dist_details=dist_details,
        )
        async for elem in message_dialog(button=None, big=True):
            with elem:
                ui.label(f"Package Info").classes("text-h5")
                tv = TreeView(self.state.visid, input_renderer=read_only_input_renderer)
                TreeGroup(
                    tv,
                    parent_path=[],
                    name="?",
                    children=info,
                    label=dist_info.dist.name,
                )

    def build_asset_nice_panels(self, asset_dist_info: DistInfo):

        @ui.refreshable
        def _render_asset_nice_panel(
            asset_dist_info: DistInfo, panel_name: str | None = None
        ):
            if panel_name is None:
                return
            self.workspace.render_nice_panel(
                asset_name=asset_dist_info.dist.name, panel_name=panel_name
            )

        panel_names = asset_dist_info.nice_panel_names
        if len(panel_names) == 1:
            panel_name = panel_names[0]
            with ui.column().classes("w-full h-full gap-0 m-0 p-2"):
                _render_asset_nice_panel(
                    asset_dist_info=asset_dist_info, panel_name=panel_name
                )
                # _render_asset_nice_panel.refresh(panel_name=panel_name)
        else:
            to_tab_name = (
                lambda n: n.replace("_panel", "").replace("_", " ").strip().title()
            )
            with ui.tabs().props("dense") as tabs:
                for panel_name in sorted(panel_names):
                    ui.tab(label=to_tab_name(panel_name), name=panel_name)
            with ui.column().classes("w-full p-2"):
                _render_asset_nice_panel(
                    asset_dist_info=asset_dist_info, panel_name=None
                )
                tabs.on_value_change(
                    lambda e, adi=asset_dist_info: _render_asset_nice_panel.refresh(
                        asset_dist_info=adi, panel_name=e.value
                    )
                )
