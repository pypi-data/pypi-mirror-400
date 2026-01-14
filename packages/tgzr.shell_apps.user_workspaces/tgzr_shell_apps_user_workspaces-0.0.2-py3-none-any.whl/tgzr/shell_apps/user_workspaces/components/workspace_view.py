from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Awaitable, cast

import dataclasses
import keyword

from nicegui import ui
import rich

from tgzr.pipeline.workspace import Workspace, DistInfo
from tgzr.nice.controls.box_selector import BoxSelector

from ..components.settings import settings_dialog
from ..settings_models import UserWorkspaceWorkspaceSettings, Repo
from .asset_graph import PackageGraph, PackageNode

from .utils import async_call_with_progress, message_dialog
from .page_state import PageState

if TYPE_CHECKING:
    from ..app import UserWorkspaceAppState, UserWorkspacesSettings

    StateType = UserWorkspaceAppState[UserWorkspacesSettings]


@dataclasses.dataclass
class Tool:
    cb: Callable[[], Awaitable[None]] | Callable[[], None]
    name: str | None = None
    icon: str | None = None
    tooltip: str | None = None
    color: str | None = None

    def render(self, tooltip: bool = True, dense: bool = False):
        btn = ui.button(self.name or "", icon=self.icon, on_click=self.cb).props(
            f"flat {dense and 'dense' or ''}"
        )
        if tooltip and self.tooltip:
            btn.tooltip(self.tooltip)
        return btn


def get_workspace_settings(state: StateType) -> UserWorkspaceWorkspaceSettings:
    # FIXME: this is illegal ! we MUST use events to set settings!
    # (but we dont have event to get a whole model)
    return state.session.settings.get_context(
        [state.session.context.user_name],
        UserWorkspaceWorkspaceSettings,
        state.workspace_settings_key,
    )


def store_workspace_settings(
    state: StateType, workspace_settings: UserWorkspaceWorkspaceSettings
) -> None:
    # FIXME: this is illegal ! we MUST use events to set settings!
    # (but we dont have event to set a whole model)
    state.session.settings.update(
        state.session.context.user_name,
        workspace_settings,
        state.workspace_settings_key,
        exclude_defaults=True,
    )


class Toolbar:

    def __init__(self, state: StateType, page_state: PageState) -> None:
        self.state = state
        self.page_state = page_state

        self.configure_tool = Tool(
            name=None,
            icon="settings_applications",
            cb=self.configure,
            tooltip="Configure Workspace",
        )

        def install_menu():
            with ui.dropdown_button("Install", icon="sym_o_download").props("flat"):
                for asset_type_name in self.page_state.asset_type_names():
                    ui.item(
                        asset_type_name,
                        on_click=lambda atn=asset_type_name: self.install_asset(atn),
                    )

        def create_menu():
            with ui.dropdown_button("Create", icon="sym_o_add_circle").props("flat"):
                for asset_type_name in self.page_state.asset_type_names():
                    ui.item(
                        asset_type_name,
                        on_click=lambda atn=asset_type_name: self.create_asset(atn),  # type: ignore
                    )

        self._tools = (
            Tool(icon="sym_o_sync", cb=self.reload, tooltip="Reload Data"),
            None,
            install_menu,
            create_menu,
            None,
            Tool(
                icon="sym_o_deployed_code_update",
                cb=self.add_external_package,
                tooltip="Add External Pacakge",
            ),
            self.configure_tool,
        )

    @ui.refreshable_method
    async def render(self):
        with ui.row().classes("w-full p-0 gap-0 xxborder xxborder-red-500"):
            for tool in self._tools:
                if tool is None:
                    ui.space()
                    continue
                if not isinstance(tool, Tool) and callable(tool):
                    tool()
                else:
                    tool.render()

    async def reload(self):
        self.page_state.events.reload_request.emit()
        self.page_state.events.reload.emit()

    async def configure(self):
        workspace = self.page_state.workspace

        def add_repo(name, path):
            print("Add Repo", name, path)

            workspace_settings = get_workspace_settings(self.state)
            workspace_settings.repos.add(Repo, name=name, path=path)
            rich.print("WS Settings:\n", workspace_settings)

            # FIXME: this is illegal ! we MUST use events to set settings!
            # (but we dont have event to set a whole model)
            store_workspace_settings(self.state, workspace_settings)

        def tmp_ui_until_we_have_model_based_settings_editor():
            with ui.column(align_items="center").classes("w-full"):
                name_i = ui.input(label="Repo Name", value="blessed").classes("grow")
                path_i = ui.input(label="Repo Path", value="LOCAL_PI").classes("grow")
                ui.button(
                    "Add this repo",
                    on_click=lambda: add_repo(name_i.value, path_i.value),
                ).classes("grow")

        await settings_dialog(
            session=self.state.session,
            visid=self.state.visid,
            settings_context=self.state.workspace_settings_context,
            settings_key=self.state.workspace_settings_key,
            settings_model=UserWorkspaceWorkspaceSettings,  # type: ignore
            title=f'Workspace "{workspace.name}" Settings',
            extra_render=tmp_ui_until_we_have_model_based_settings_editor,
        )

    async def install_asset(self, asset_type):
        print("install {asset_type} Asset...")

    async def more_asset_tools(self):
        print("More Asset Tools...")

    async def install_tool(self):
        print("Add Asset...")

    async def more_tool_tools(self):
        print("More tools...")

    async def create_asset(self, asset_type_name: str):
        workspace = self.page_state.workspace

        workspace_settings = get_workspace_settings(self.state)
        # FIXME: syncing the repo in the workspace should be done at a better time
        # maybe even done the other way around ?
        for repo in workspace_settings.repos.items:
            workspace.add_repo(repo.name, repo.path + "/" + repo.name)

        repo_names = workspace.repo_names()
        if not repo_names:
            async for elem in message_dialog(button=None):
                with elem:
                    ui.label("You must configure an Asset Repository first.")
                    with ui.row().classes("w-full"):
                        ui.space()
                        btn = self.configure_tool.render(tooltip=False)
                        btn.props(remove="flat")
                        btn.set_text("Configure Workspace")
                        ui.space()
            return

        def name_validation(value: str):
            package_name = value.lower().replace("-", "_")
            if keyword.iskeyword(package_name):
                return "Forbidden Keyword"
            if not value.replace(".", "").isidentifier():
                return "Invalid Identifier"

        with ui.dialog() as dialog, ui.card():
            name_input = ui.input(label="Asset Name", validation=name_validation)
            default_repo_input = ui.select(repo_names)
            with ui.row().classes("w-full"):
                ui.space()
                ui.button(
                    "Create",
                    on_click=lambda: dialog.submit(
                        (name_input.value, default_repo_input.value)
                    ),
                )

        result = await dialog
        if result is not None:
            name, repo = result
            if self.page_state.workspace is None:
                raise Exception("No Workspace ?!?")
            try:
                await async_call_with_progress(
                    self.page_state.workspace.create_asset, asset_type_name, name
                )
            except Exception as err:
                self.page_state.events.on_exception.emit(err)
                # ui.notify(err, type="negative", position="top")
        dialog.clear()
        self.page_state.events.reload.emit()

    async def add_external_package(self):
        print("add_external_package... should be in workspace settings!")


def scroll_area():
    # TODO: add this in tgzr.nice !
    sa = ui.scroll_area().classes("no-content-padding-scroll-area")
    r = ui.query(f"#c{sa.id} .q-scrollarea__content").classes(
        "p-2 pr-4 gap-0 bg-neutral-800"  # bg-transparent does not work D,:
    )
    return sa


def list_group(title: str, icon: str = "sym_o_folder"):
    # TODO: add this in tgzr.nice !
    with ui.column().classes("w-full pb-4 p-0 gap-0"):
        with ui.row(align_items="center").classes(
            "w-full cursor-pointer gap-1"
        ) as header:
            header.on("click", lambda: toggle())
            ui.icon(icon, size="sm").classes("opacity-50")
            ui.label(title)
        content = ui.column().classes("w-full gap-0 pl-4")

    def toggle():
        content.visible = not content.visible

    return content


class Outliner:
    def __init__(self, state: StateType, page_state: PageState) -> None:
        self.state = state
        self.page_state = page_state
        self._group_assets_by = "asset_type"

        self.page_state.events.current_changed.subscribe(self._on_current_changed)

        self._asset_rows: dict[str, ui.row] = {}
        self._current_dist_name: str | None = None

    def _on_current_changed(self, dist_name: str | None):
        classes = "!bg-neutral-700"
        if self._current_dist_name is not None:
            row = self._asset_rows.get(self._current_dist_name)
            if row is not None:
                row.classes(remove=classes)
        self._current_dist_name = dist_name
        if self._current_dist_name is not None:
            try:
                row = self._asset_rows[self._current_dist_name]
            except KeyError as err:
                # print("???", dist_name, self._asset_rows.keys())
                self.page_state.events.on_exception.emit(err)
            else:
                row.classes(add=classes)

    @ui.refreshable_method
    async def render(self):
        settings = self.state.app_settings()
        with ui.column().classes("w-full h-full p-0"):
            with ui.tabs().classes("w-full") as tabs:
                asset_tab = ui.tab(
                    settings.show_lib_packages and "Packages" or "Assets"
                )
                files_tab = ui.tab("Files")
            with ui.tab_panels(tabs, value=asset_tab).classes("w-full h-full"):
                with ui.tab_panel(asset_tab).classes("p-0"):
                    with ui.row().classes("w-full h-full p-0"):
                        with scroll_area().classes("w-full h-full"):
                            await self.render_asset_panel()
                with ui.tab_panel(files_tab).classes("p-0"):
                    with ui.row().classes("w-full h-full p-0"):
                        with scroll_area().classes("w-full h-full"):
                            await self.render_files_panel()

    def _asset_row(self, dist_info: DistInfo):
        with ui.row(wrap=False, align_items="center").classes(
            "w-full gap-0 bg-neutral-800"
        ) as row:
            row.classes("hover:brightness-120")
            self._asset_rows[self.page_state.canonicalize_name(dist_info.dist.name)] = (
                row
            )
            asset_name = dist_info.asset_name
            show_dist = lambda dn=dist_info.dist.name: self.page_state.events.show_dist.emit(
                dn  # type: ignore
            )
            ui.label(asset_name).classes("cursor-pointer px-2").on("click", show_dist)
            vchip = ui.chip(
                "v" + dist_info.dist.version,
                on_click=lambda dn=dist_info.dist.name: self.page_state.events.show_dist_info.emit(
                    dn  # type: ignore
                ),
            ).props("dense outline")
            if dist_info.is_editable:
                vchip.props["color"] = "orange"
            ui.space().classes("h-[1em] cursor-pointer").on("click", show_dist)
            with ui.row(wrap=False).classes("gap-0"):
                if dist_info.is_editable:
                    ui.button(icon="sym_o_build").props("flat dense").tooltip("Build")
                    ui.button(icon="sym_o_publish").props("flat dense").tooltip(
                        "Publish"
                    )

    def _get_asset_group_names(self, dist_info) -> list[str] | None:
        if self._group_assets_by == "tags":
            return list(dist_info.tags)
        elif self._group_assets_by == "asset_type":
            return [dist_info.asset_type]
        return None

    def asset_group_icon(self, asset_group_name):
        return dict(
            tags="sym_o_sell",
            asset_type="sym_o_category",
        ).get(asset_group_name, "sym_o_folder")

    def ungroup_assets(self):
        self._group_assets_by = None
        self.render_asset_panel.refresh()

    def group_assets_by_tag(self):
        self._group_assets_by = "tags"
        self.render_asset_panel.refresh()

    def group_assets_by_type(self):
        self._group_assets_by = "asset_type"
        self.render_asset_panel.refresh()

    def group_assets_by(self, dist_info_name: str) -> None:
        self._group_assets_by = dist_info_name
        self.render_asset_panel.refresh()

    @ui.refreshable_method
    async def render_asset_panel(self):
        self._asset_rows.clear()
        with ui.row(align_items="center").classes("w-full gap-0"):
            # ui.space()
            for group_by, icon, tooltip in (
                (None, "sym_o_list", "List"),
                ("tags", "sym_o_sell", "Group by Tag"),
                ("asset_type", "sym_o_category", "Group by Type"),
            ):
                b = (
                    ui.button(
                        icon=icon,
                        on_click=lambda g=group_by: self.group_assets_by(g),  # type: ignore
                        color="W",
                    )
                    .props("dense")
                    .classes("opacity-50")
                    .tooltip(tooltip)
                )
                if self._group_assets_by != group_by:
                    b.props("flat")

        groups = {}
        dist_infos = [
            self.page_state.workspace.get_dist_info(dist)
            for dist in await self.page_state.dists()
        ]
        dist_infos.sort(key=lambda di: di.asset_name.lower())
        settings = self.state.app_settings()
        for dist_info in dist_infos:
            if not settings.show_lib_packages and not dist_info.is_asset:
                continue
            group_names = self._get_asset_group_names(dist_info)
            if group_names is not None:
                for group_name in group_names:
                    group = groups.get(group_name)
                    if group is None:
                        group = list_group(
                            (group_name and group_name + "s") or "Others",
                            icon=self.asset_group_icon(self._group_assets_by),
                        )
                        groups[group_name] = group
                    with group:
                        self._asset_row(dist_info)
            else:
                self._asset_row(dist_info)

        self._on_current_changed(self._current_dist_name)

    @ui.refreshable_method
    async def render_files_panel(self):
        with ui.row():
            self.state.visid.icon()
            ui.label("Comming soon...")


class VenvView:
    def __init__(self, state: StateType, page_state: PageState) -> None:
        self.state = state
        self.page_state = page_state
        self._pinned_pos: dict[str, tuple[int, int]] = {}

        self._graph: PackageGraph | None = None

        self.page_state.events.reload_request.subscribe(self._before_reload)
        self.page_state.events.shown_dists_changed.subscribe(self.update_shown_dists)
        # self.page_state.events.layout.subscribe(self.layout)

        self._tools = [
            Tool(icon="fa-solid fa-sitemap", tooltip="Crappy Layout", cb=self.layout),
            None,
            Tool(icon="sym_o_zoom_in", cb=self.zoom_in),
            Tool(icon="sym_o_zoom_out", cb=self.zoom_out),
        ]

    @property
    def graph(self) -> PackageGraph:
        if self._graph is None:
            raise RuntimeError("graph is not yet built.")
        return self._graph

    async def _before_reload(self):
        await self._update_pinned_pos()

    async def _update_pinned_pos(self) -> None:
        self._pinned_pos = await self.graph.get_nodes_positions(
            [d.name for d in self.page_state.shown_dists]
        )

    async def update_shown_dists(self):
        await self._update_pinned_pos()
        await self.render.refresh()

    async def layout(self):
        await self._update_pinned_pos()
        await self.graph.layout(self._pinned_pos)

    async def zoom_in(self):
        await self.graph.scale_layout(2)

    async def zoom_out(self):
        await self.graph.scale_layout(0.5)

    @ui.refreshable_method
    async def render(self):
        with ui.column().classes("w-full h-full p-4 gap-0"):
            with ui.row().classes("p-0 gap-0 w-full flex-row-reverse"):
                for tool in self._tools:
                    if tool is None:
                        ui.separator().props("vertical")
                        continue
                    tool.render(dense=True)

            with BoxSelector() as selector:

                self._graph = PackageGraph[PackageNode](
                    self.state, self.page_state
                ).classes("w-full h-full")

                selector.on_box_selected(self._graph.handle_box_selection)

                nodes: dict[str, PackageNode] = {}
                with self._graph:
                    dists = self.page_state.shown_dists  # await self.venv_data.dists()
                    x = 500
                    y = 100
                    for dist in dists[:10]:
                        pos = [x, y]
                        try:
                            pos = self._pinned_pos[dist.name]
                        except KeyError:
                            pass
                        node = PackageNode(self._graph, dist, *pos)
                        node.open()
                        node.show_pinned()
                        x += 100
                        if x > 1000:
                            x = 0
                            y += 100
                        nodes[node.props["id"]] = node

                pos = [x - 300, y]
                for node_id, node in nodes.items():
                    known_pos = self._pinned_pos.get(node_id)
                    pos = known_pos and list(known_pos) or pos
                    await self._graph.load_requires(node, pos)

            self._graph.updateNodesAndPorts()


def get_workspace_instance(state: StateType) -> Workspace | None:
    if state.workspace_name is None:
        return None

    project = state.session.get_selected_project()
    if project is None:
        return None

    workspace_path = project.work.user_path / state.workspace_name
    workspace = Workspace(workspace_path)
    return workspace


async def workspace_renderer(state: StateType):
    workspace = get_workspace_instance(state)

    def on_exception(exception):
        rich.print(exception)
        ui.notify(str(exception), type="negative", position="top")

    page_state = PageState(state, workspace)
    page_state.events.on_exception.subscribe(on_exception)

    venv_view = VenvView(state, page_state)
    toolbar = Toolbar(state, page_state)
    outliner = Outliner(state, page_state)

    @ui.refreshable
    async def render_all():
        page_state.clear_cache()
        with ui.column().classes("w-full h-full p-4 gap-0"):
            if workspace is None:
                ui.label("Oops... no workspace ?!?")
                return

            workspace.ensure_exists()
            await toolbar.render()
            ui.separator()
            with ui.splitter(value=20).classes("w-full h-full") as splitter:
                with splitter.before:
                    await outliner.render()
                with splitter.after:
                    await venv_view.render()

    await render_all()
    page_state.events.reload.subscribe(render_all.refresh)
