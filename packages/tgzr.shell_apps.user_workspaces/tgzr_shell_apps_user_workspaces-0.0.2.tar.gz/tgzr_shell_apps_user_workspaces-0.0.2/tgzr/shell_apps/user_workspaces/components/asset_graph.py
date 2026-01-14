from __future__ import annotations
from typing import TYPE_CHECKING

from importlib.metadata import Distribution
from packaging.requirements import Requirement

from nicegui import ui

from tgzr.nice.data_elements.node_graph import NodeGraph, GraphNode, NodePort

from .page_state import PageState

if TYPE_CHECKING:
    from ..app import UserWorkspaceAppState, UserWorkspacesSettings

    StateType = UserWorkspaceAppState[UserWorkspacesSettings]


class PackageGraph[NodeType: PackageNode](NodeGraph["PackageNode"]):
    def __init__(self, state: StateType, page_state: PageState):
        super().__init__()
        self.state = state
        self.page_state = page_state

        settings = self.state.app_settings()
        self.open_node_on_select = settings.open_node_on_select
        self.open_node_on_hover = settings.open_node_on_hover
        self.show_lib_packages = settings.show_lib_packages

    async def unload_required_by(self, node: PackageNode, max_depth: int = -1):
        for node in self.get_nodes_from(node.props["id"], "self"):
            if max_depth < 0 or max_depth > 1:
                await self.unload_requires(node, max_depth=max_depth - 1)
            self.delete_node(node)

    async def load_required_by(
        self, node: PackageNode, pos: list[int], max_depth: int = 2
    ):
        # NB: pos is edited in place

        new_nodes = []
        existing_nodes = []
        self_reqs = await self.page_state.get_required_by(node.dist)
        for self_req in self_reqs:
            source_node = self.get_node(
                self.page_state.canonicalize_name(self_req.name)
            )
            if source_node is None:
                if max_depth == 0:
                    continue
                with self:
                    source_node = PackageNode(self, self_req, *pos)
                    await source_node.load_inputs()
                    new_nodes.append(source_node)
                    pos[1] += 100
            else:
                existing_nodes.append(source_node)
                self.set_node_position(source_node.props["id"], *pos)
                pos[1] += 100
            self.connect(
                node.props["id"],
                source_node.props["id"],
                "bezier",
                from_port="self",
                to_port="require",
            )

        for node in new_nodes:
            await node.load_inputs()
            await node.load_outputs()

        if max_depth > 1:
            pos[1] += 200
            for new_node in new_nodes:
                await self.load_required_by(new_node, pos, max_depth - 1)

    async def unload_requires(self, node: PackageNode, max_depth: int = -1):
        for node in self.get_nodes_to(node.props["id"], "require"):
            if max_depth < 0 or max_depth > 1:
                await self.unload_requires(node, max_depth=max_depth - 1)
            self.delete_node(node)

    async def load_requires(
        self, node: PackageNode, pos: list[int], max_depth: int = 2
    ):
        # NB: pos is edited in place

        new_nodes = []
        existing_nodes = []
        req_dists = await self.page_state.get_required(node.dist)
        for req_dist in req_dists:
            req_dist_info = self.page_state.workspace.get_dist_info(req_dist)
            req_dist_name = self.page_state.canonicalize_name(req_dist.name)
            if not self.show_lib_packages and not req_dist_info.is_asset:
                continue
            req_node = self.get_node(req_dist_name)
            if req_node is None:
                if max_depth == 0:
                    continue
                with self:
                    req_node = PackageNode(self, req_dist, *pos)
                    new_nodes.append(req_node)
                    pos[1] += 100
            else:
                existing_nodes.append(req_node)
                self.set_node_position(req_node.props["id"], *pos)
                pos[1] += 100
            self.connect(
                req_node.props["id"],
                node.props["id"],
                "bezier",
                from_port="self",
                to_port="require",
            )

        for node in new_nodes:
            await node.load_inputs()
            await node.load_outputs()

        if max_depth > 1:
            for new_node in new_nodes:
                await self.load_requires(new_node, pos, max_depth - 1)


class PackageNode(GraphNode["PackageGraph[PackageNode]"]):
    def __init__(
        self,
        graph: PackageGraph[PackageNode],
        dist: Distribution,
        x: float = 0,
        y: float = 0,
    ):
        if dist.name == None:
            raise Exception(f"Dist.name is None!!! {self.dist}")

        # NB: these are needed *before* super()__init__()
        self.dist = dist
        self.dist_info = graph.page_state.workspace.get_dist_info(dist)
        self.asset_type_info = graph.page_state.asset_type_info(self.dist_info)
        self.badge = None

        super().__init__(graph, graph.page_state.canonicalize_name(dist.name), x, y)
        self._graph = graph  # update type GraphNode->PackageGraph in completion

        self.classes("shadow-xl")
        self.requires = []
        self.requires = dist.requires

        self._lock_open = False

        self.close()

    @property
    def graph(self) -> PackageGraph:
        # update type in code completion
        return self._graph

    async def load_inputs(self):
        self_reqs = await self.graph.page_state.get_required_by(self.dist)
        for self_req in self_reqs:
            self_req = self.graph.page_state.canonicalize_name(self_req.name)
            source_node = self.graph.get_node(self_req)
            if source_node is not None:
                self.graph.connect(
                    self.props["id"],
                    source_node.props["id"],
                    "bezier",
                    "self",
                    "require",
                    self.asset_type_info.color,
                    source_node.asset_type_info.color,
                )

    async def load_outputs(self):
        req_dists = await self.graph.page_state.get_required(self.dist)
        for req_dist in req_dists:
            req_dist_name = self.graph.page_state.canonicalize_name(req_dist.name)
            req_node = self.graph.get_node(req_dist_name)
            if req_node is not None:
                self.graph.connect(
                    req_node.props["id"],
                    self.props["id"],
                    "bezier",
                    "self",
                    "require",
                    req_node.asset_type_info.color,
                    self.asset_type_info.color,
                )

    def show_info(self):
        self.graph.page_state.events.show_dist_info.emit(self.dist.name)
        print("SHOWN INFO FOR NODE", self.props["id"])

    # def _build_menu(self):
    #     with ui.button(icon="menu").props("flat dense"):
    #         with ui.menu() as menu:
    #             ui.menu_item(
    #                 "Add Input",
    #                 lambda: self.graph.page_state.events.add_input.emit(self.dist.name),
    #             )
    #             ui.menu_item(
    #                 "Do Something",
    #                 lambda: self.content.set_visibility(not self.content.visible),
    #             )
    #             ui.menu_item("Blah", lambda e: self.show_info())
    #             ui.separator()
    #             ui.menu_item("Close", menu.close)

    def _build_header(self):
        self.toggle_btn = ui.button(
            icon="sym_o_arrow_right", on_click=self.toggle_content
        ).props("flat dense round color='W'")
        if self.asset_type_info.icon is not None:
            with ui.badge(color=self.asset_type_info.color).classes(
                f"bg-[{self.asset_type_info.color}]"
            ) as self.badge:
                ui.icon(self.asset_type_info.icon).tooltip(
                    self.asset_type_info.category
                )
        ui.label(self.dist_info.asset_name).classes(
            add=f"opacity-50 hover:opacity-100",
            remove="text-T",
        )
        vchip = ui.chip(
            "v" + self.dist_info.dist.version,
            # on_click=lambda dn=self.dist_info.dist.name: self.graph.page_state.events.bump.emit(
            #     dn  # type: ignore
            # ),
        ).props("dense outline")
        if self.dist_info.is_editable:
            vchip.props["color"] = "orange"
        # self._build_menu()
        ui.space().classes("min-w-[1em]")

    def _build_content(self):
        panel_names = []
        if self.dist_info.is_asset and self.dist_info.nice_panel_names:
            panel_names = self.dist_info.nice_panel_names

        with ui.row(wrap=False).classes("gap-1 w-full"):

            # Entry Point Tools
            with ui.row(wrap=False).classes(
                "gap-0 border border-neutral-600 rounded-sm"
            ):
                for ep in self.dist.entry_points.select(group="console_scripts"):
                    name = ep.name
                    icon = "sym_o_terminal"
                    if ep.name == self.dist.name:
                        # self execute convention
                        name = "Execute"
                        icon = "sym_o_run_circle"
                    elif ep.name == "tgzr.pipeline.asset.build":
                        name = "Build"
                        icon = "sym_o_build_circle"
                    elif ep.name == "tgzr.pipeline.asset.create":
                        name = "Create"
                        icon = "sym_o_plumbing"
                    ui.button(
                        icon=icon,
                        on_click=lambda epn=ep.name: self.execute_console_script(epn),
                    ).props("flat dense").tooltip(name)

            # Editable Asset Tools
            if self.dist_info.is_asset and self.dist_info.is_editable:
                with ui.row(wrap=False).classes(
                    "gap-0 border border-neutral-600 rounded-sm"
                ):
                    if self.asset_type_info.type_name == "Workscene":
                        ui.button(icon="edit").props("dense").tooltip("Edit")
                    ui.button(icon="repartition").props("flat dense").tooltip("Export")
                    ui.button(icon="publish").props("flat dense").tooltip("Publish")
                    ui.button(
                        icon="sym_o_keyboard_double_arrow_up",
                        on_click=lambda dn=self.dist_info.dist.name: self.graph.page_state.events.bump.emit(
                            dn  # type: ignore
                        ),
                    ).props("flat dense").tooltip("Bump Version")

            ui.space()

            # Info Button
            ui.button(icon="sym_o_info", on_click=self.show_info).props(
                "flat dense"
            ).classes("opacity-50").tooltip("Print Debug Info")

            # Panels On/Off
            if panel_names:
                panels_toggle = (
                    ui.button(icon="sym_o_bottom_panel_close")
                    .props("dense flat")
                    .tooltip("Show/Hide Panels")
                )

        # Asset Nice Panels
        if panel_names:
            with ui.column().classes(
                "w-full gap-0 p-0 border border-neutral-600 rounded-sm"
            ) as panels_box:
                # NOTE: tell the Asset GUI developers to add this to ui elements
                # when they need the element to consume mouse event instead
                # of the graph (pan handler):
                #   your_element.on(
                #         "mousedown", js_handler="(e)=>{console.log(e); e.stopPropagation()}"
                #   )
                # We could do it here for the whole panel_box, but panning the view
                # from the panel background is too satifying to remove :}
                panels_box.visible = False
                self.graph.page_state.build_asset_nice_panels(self.dist_info)
            panels_toggle.on_click(
                lambda: panels_box.set_visibility(not panels_box.visible)
            )

        # Tags
        if self.dist_info.tags:
            with ui.row().classes("gap-0 p-0"):
                for tag in self.dist_info.tags:
                    ui.chip(tag).props("dense outline")

    def _build(self):
        with ui.row(wrap=False, align_items="center").classes(
            "w-full p-0 gap-0"
        ) as all:
            with ui.column(align_items="end").classes(
                "gap-0 absolute end-full"
            ) as self.input_ports:
                self.require_port = DistInPort(self, "require")
                # DistInPort("build")
                # DistInPort("export")
                # DistInPort("publish")

            with ui.column().classes("w-full gap-0"):
                with ui.row(wrap=False, align_items="center").classes(
                    f"gap-1  bg-neutral-500 rounded-t-lg shadow-lg w-full cursor-grab"
                ) as self._header:
                    self._build_header()
                    if self.graph.open_node_on_hover:
                        self._header.on("mouseenter", self.open)
                with ui.row().classes("bg-neutral-700 gap-1 p-1 rounded-b-lg w-full"):
                    with ui.column().classes("w-full gap-1") as self.content:
                        self._build_content()

            with ui.column(align_items="start").classes(
                "gap-0 absolute left-full"
            ) as self.output_ports:
                self.self_out_port = DistOutPort(self, "self")
        if self.graph.open_node_on_hover:
            all.on("mouseleave", self.close)

    def open(self):
        if not self.content.visible:
            self.toggle_content()

    def close(self):
        if self._lock_open:
            return
        if self.content.visible:
            self.toggle_content()

    def toggle_content(self):
        self.content.visible = not self.content.visible
        if self.content.visible:
            self.toggle_btn.icon = "arrow_drop_down"
            self.classes(add="z-10")
        else:
            self.toggle_btn.icon = "arrow_right"
            self.classes(remove="z-10")
        self.graph.updateNodesAndPorts()

    def show_pinned(self):
        with self._header:
            icon = ui.icon("sym_o_keep", size="xs").classes("opacity-50")
            # icon.move(target_index=0)

    def set_selected(self, b: bool):
        self.graph.page_state.events.current_changed.emit(self.props["id"])
        self_classes = "z-10"
        header_classes = f"border-b-6 border-[{self.asset_type_info.color}]"
        # badge_classes = f"!bg-{self._asset_type_color}-400"
        badge_classes = f"brightness-150"

        if b:
            self.classes(add=self_classes)
            self._header.classes(add=header_classes)
            if self.badge is not None:
                self.badge.classes(add=badge_classes)

            self._lock_open = True
            if self.graph.open_node_on_select:
                self.open()
        else:
            self.classes(remove=self_classes)
            self._header.classes(remove=header_classes)
            if self.badge is not None:
                self.badge.classes(remove=badge_classes)
            self._lock_open = False
            if self.graph.open_node_on_select:
                self.close()

    async def show_my_requires(self):
        my_pos = await self.graph.get_nodes_positions([self.props["id"]])
        x, y = my_pos[self.props["id"]]
        x -= 200
        await self.graph.load_requires(self, [x, y], 1)

    async def hide_my_requires(self):
        await self.graph.unload_requires(self, 1)

    async def show_my_required_by(self):
        my_pos = await self.graph.get_nodes_positions([self.props["id"]])
        x, y = my_pos[self.props["id"]]
        x += 200
        await self.graph.load_required_by(self, [x, y], 1)

    async def hide_my_required_by(self):
        await self.graph.unload_required_by(self, 1)

    async def execute_console_script(self, console_script_name: str):
        self.graph.page_state.events.execute_console_script.emit(
            self.dist.name, console_script_name
        )


class _DistPort(NodePort["PackageNode"]):
    DOT_CLASSES = ""
    ACTIONS_PARENT_CLASSES = ""
    TOP_CLASSES = ""

    def __init__(self, node: PackageNode, port_id: str):
        super().__init__(node, port_id)
        self._node = node  # update type in code completion

    @property
    def node(self) -> PackageNode:
        # update type in code completion
        return self._node

    def toggle(self):
        if "invisible" in self._action_parent.classes:
            self.open()
        else:
            self.close()

    def open(self):
        # self._action_parent.visible = True
        self._action_parent.classes(remove="invisible")

    def close(self):
        self._action_parent.classes(add="invisible")
        # self._action_parent.visible = False
        # self._action_parent.classes(remove="p-2 border-y")

    def _build(self) -> ui.element:
        with ui.row(wrap=False, align_items="center").classes(self.TOP_CLASSES):
            dot = ui.element().classes("w-[.5em] h-[1em] node-port-center")
            dot.classes(add=self.DOT_CLASSES)
            color = self.node.asset_type_info.color
            dot.classes(
                add=f"bg-[{color}] brightness-50 hover:brightness-100 cursor-pointer"
            )
            self._action_parent = (
                ui.row(wrap=False, align_items="center")
                .classes(self.ACTIONS_PARENT_CLASSES)
                .classes("opcatity-0")
                .props("rtl")
            )
            self._action_parent.classes(add="invisible")
            dot.on("mouseenter", self.open)
            self.on("mouseleave", self.close)
        return dot

    def add_action(self, name, icon, cb):
        with self._action_parent:
            if icon is None:
                ui.label(name)
            else:
                ui.button(icon=icon, color="W", on_click=cb).props(
                    "flat dense"
                ).tooltip(name)


class DistInPort(_DistPort):
    TOP_CLASSES = "gap-0 flex-row-reverse"
    ACTIONS_PARENT_CLASSES = "gap-0"
    DOT_CLASSES = "rounded-l-full"

    def __init__(self, node: PackageNode, port_id: str):
        super().__init__(node, port_id)

        self.add_action(
            f"Show {self._props["data-port-id"]}s",
            "sym_o_input",  # "fa-solid fa-arrow-right-to-bracket",
            self.node.show_my_requires,
        )
        self.add_action(
            f"Hide {self._props["data-port-id"]}s",
            "fa-regular fa-hand-scissors",
            self.node.hide_my_requires,
        )
        self.add_action(
            f"Edit {self._props["data-port-id"]}s",
            "sym_o_edit_square",
            lambda: self.node.graph.page_state.events.add_input.emit(
                self.node.dist.name
            ),
        )


class DistOutPort(_DistPort):
    TOP_CLASSES = "gap-0"
    ACTIONS_PARENT_CLASSES = "gap-0 flex-row-reverse"
    DOT_CLASSES = "rounded-r-full"

    def __init__(self, node: PackageNode, port_id: str):
        super().__init__(node, port_id)

        self._conected_nodes: list[PackageNode] = []

        self.add_action(
            "Show Connected",
            "sym_o_output",  # "fa-solid fa-arrow-right-from-bracket",
            self.node.show_my_required_by,
        )
        self.add_action(
            "Hide Connected",
            "fa-regular fa-hand-scissors",
            self.node.hide_my_required_by,
        )
        self.add_action(
            f"Edit Connections",
            "sym_o_edit_square",
            lambda: ui.notify("Not implemented...", position="top"),
        )
