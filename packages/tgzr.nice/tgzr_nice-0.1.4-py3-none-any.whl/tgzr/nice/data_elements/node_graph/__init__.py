from __future__ import annotations
from typing import Self, List, Dict, Any, Literal, Optional

from collections import namedtuple

from nicegui import ui

WireStyle = Literal["straight", "curved", "bezier"]

Wire = namedtuple("Wire", "from_id to_id style from_port to_port, from_color to_color")


# async def test():
#     from tgzr.nice.controls.box_selector import BoxSelector

#     def handle_selection(e):
#         print(e)
#         x, y = e.args["x"], e.args["y"]
#         w, h = e.args["width"], e.args["height"]
#         ui.notify(f"Selected: {w:.0f}×{h:.0f} at ({x:.0f}, {y:.0f})")

#     with ui.element().classes("w-100 h-100 border-2 border-blue-500"):
#         ui.label("Hold Shift and drag to select")

#         with BoxSelector().classes("w-full h-96 border-2 border-red-500") as selector:
#             selector.on_box_selected(handle_selection)

#             # Add any content
#             ui.label("Content 1").classes(
#                 "xabsolute top-10 left-10 bg-blue-500 text-white p-4"
#             )
#             ui.label("Content 2").classes(
#                 "xabsolute top-32 left-40 bg-green-500 text-white p-4"
#             )
#             ui.button("Click me").classes("xabsolute top-64 left-20")

#     return


class NodeGraph[NodeType: GraphNode](ui.element, component="node_graph.js"):
    def __init__(self):
        """
        A graph with nodes connected thru ports or the node itself.

        Supports nested nodes.
        """
        super().__init__()
        self._nodes: dict[str, NodeType] = {}
        self._selected_node_ids: set[str] = set()
        self._wires: set[Wire] = set()
        self._props["wires"] = []

        self.on("node_moved", self._handle_node_moved)
        self.on("node_clicked", self._handle_node_clicked)

    async def handle_box_selection(self, e):
        # print(e)
        # x, y = e.args["x"], e.args["y"]
        # w, h = e.args["width"], e.args["height"]
        # ui.notify(f"Selected: {w:.0f}×{h:.0f} at ({x:.0f}, {y:.0f})")
        sel_x = e.args["x"]
        sel_y = e.args["y"]
        sel_width = e.args["width"]
        sel_height = e.args["height"]

        # Call JavaScript method to get selected nodes
        selected = await self.run_method(
            "getNodesInRect", sel_x, sel_y, sel_width, sel_height
        )

        if selected:
            [
                self.toggle_select(self.get_node(info["id"]), replace_selected=False)
                for info in selected
            ]
            # node_ids = [node["id"] for node in selected]
            # ui.notify(f'Selected {len(node_ids)} nodes: {", ".join(node_ids)}')
            # return node_ids
        return []

    def _register_node(self, node: NodeType):
        self._nodes[node.props["id"]] = node

    def _handle_node_moved(self, e):
        pass

    def _handle_node_clicked(self, e):
        node_id = e.args["nodeId"]
        try:
            node = self._nodes[node_id]
        except KeyError:
            raise  # casualy shrugging...
        self.toggle_select(node, replace_selected=not e.args["shiftKey"])

    def clear_selection(self):
        for nid in self._selected_node_ids:
            n = self._nodes.get(nid)
            if n is not None:
                n.set_selected(False)
        self._selected_node_ids.clear()

    def toggle_select(self, node, replace_selected: bool = True):
        node_id = node.props["id"]
        if node_id in self._selected_node_ids:
            if not replace_selected:
                node.set_selected(False)
                self._selected_node_ids.remove(node_id)
        else:
            if replace_selected:
                self.clear_selection()
            self._selected_node_ids.add(node_id)
            node.set_selected(True)

    def updateNodesAndPorts(self) -> None:
        """Call this if you need to update the wires drawing."""
        self.run_method("updateNodesAndPorts")

    def get_node(self, node_id: str) -> NodeType | None:
        return self._nodes.get(node_id, None)

    async def get_nodes_positions(
        self, node_ids: list[str]
    ) -> dict[str, tuple[int, int]]:
        return await self.run_method("getNodePositions", node_ids)

    def set_node_position(self, node_id, x, y):
        self.run_method("set_node_pos", node_id, x, y)

    def move_node(self, node_id, ox, oy):
        self.run_method("move_node", node_id, ox, oy)

    def get_nodes_from(self, node_id: str, from_port: str | None):
        return [
            self._nodes[w.to_id]
            for w in self._wires
            if w.from_id == node_id and w.from_port == from_port
        ]

    def get_nodes_to(self, node_id: str, to_port: str | None):
        return [
            self._nodes[w.from_id]
            for w in self._wires
            if w.to_id == node_id and w.to_port == to_port
        ]

    def get_inputs(self, node_id: str):
        return [w.from_id for w in self._wires if w.to_id == node_id]

    def get_outputs(self, node_id: str):
        return [w.to_id for w in self._wires if w.from_id == node_id]

    def delete_node(self, node):
        node_id = node.props["id"]
        del self._nodes[node_id]

        self._wires = set(
            [w for w in self._wires if not (w.from_id == node_id or w.to_id == node_id)]
        )
        self._sync_wires()
        node.delete()

    def connect(
        self,
        from_id: str,
        to_id: str,
        style: WireStyle = "straight",
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        from_color: str | None = None,
        to_color: str | None = None,
    ):
        """
        If the connection already exists, nothing is done.
        """
        w = Wire(
            from_id=from_id,
            to_id=to_id,
            from_port=from_port,
            to_port=to_port,
            style=style,
            from_color=from_color,
            to_color=to_color,
        )
        if w in self._wires:
            return
        self._wires.add(w)
        self._sync_wires()

    def _sync_wires(self):
        self._props["wires"] = [w._asdict() for w in self._wires]
        self.update()

    def remove_connection(self, from_id: str, to_id: str):
        self._wires = set(
            [w for w in self._wires if not (w.from_id == from_id and w.to_id == to_id)]
        )
        self._sync_wires()
        # self._props["wires"] = [
        #     w
        #     for w in self._props["wires"]
        #     if not (w["from"] == from_id and w["to"] == to_id)
        # ]
        # self.update()

    # def get_connection(self) -> List[Dict[str, Any]]:
    #     return self._props["wires"]

    async def layout(self, pinned_node_pos: dict[str, tuple[int, int]]):
        """
        Note: this layout sucks.
        Also, you need to install networkx to use it.

        We'll add a proper layout implementation if needed.
        """

        import networkx

        G = networkx.DiGraph()
        G.add_edges_from(
            [
                (f"{w.from_id}.{w.from_port}", f"{w.to_id}.{w.to_port}")
                for w in self._wires
            ]
        )
        req_to_node = [
            (f"{node_id}.require", f"{node_id}") for node_id in self._nodes.keys()
        ]
        node_to_self = [
            (f"{node_id}", f"{node_id}.self") for node_id in self._nodes.keys()
        ]
        G.add_edges_from(req_to_node + node_to_self)

        pinned_node_ids = list(pinned_node_pos.keys())
        pos = networkx.spring_layout(
            G,
            k=100,
            scale=1,
            pos=pinned_node_pos or None,
            fixed=pinned_node_ids or None,
        )
        self.apply_layout(pos)  # type: ignore

    def apply_layout(
        self,
        positions: Dict[str, tuple],
        scale: float = 1.0,
        center_x: float = 0,
        center_y: float = 0,
    ):
        for node_id, (x, y) in positions.items():
            if node_id in self._nodes:
                scaled_x = x * scale + center_x
                scaled_y = y * scale + center_y
                self.set_node_position(node_id, scaled_x, scaled_y)

        self.updateNodesAndPorts()

    async def scale_layout(self, scale: float):
        if not self._selected_node_ids:
            nodes_ids = list(self._nodes.keys())
        elif len(self._selected_node_ids) == 1:
            nodes_ids = set(self._nodes.keys())
            nodes_ids -= self._selected_node_ids
            nodes_ids = list(nodes_ids)
        else:
            nodes_ids = list(self._selected_node_ids)
        current_position = await self.get_nodes_positions(nodes_ids)
        self.apply_layout(current_position, scale=scale)


class GraphNode[GraphType: NodeGraph](ui.element):
    """A draggable node in the graph. Use as a container for your content."""

    def __init__(self, graph: GraphType, node_id: str, x: float = 0, y: float = 0):
        """
        Create a graph node.

        Args:
            node_id: Unique identifier for this node
            x: Initial x position (relative to parent)
            y: Initial y position (relative to parent)
        """
        super().__init__("div")

        self._props["id"] = f"{node_id}"
        self._props["data-node-id"] = node_id
        self._props["data-x"] = x
        self._props["data-y"] = y

        self._graph = graph
        self._graph._register_node(self)

        # Default styling for graph nodes
        self.classes("graph-node")
        self.classes("absolute")
        # self._style["position"] = "absolute"
        self._style["transform"] = f"translate({x}px, {y}px)"
        # self._style["cursor"] = "move"
        self._style["user-select"] = "none"

        with self:
            self._build()

    @property
    def graph(self) -> NodeGraph[Self]:
        return self._graph

    def _build(self):
        ui.label(self._props["id"]).classes("text-xl")

    def set_selected(self, b: bool):
        pass


class NodePort[NodeType: GraphNode](ui.element):
    """A connection point on a node."""

    def __init__(self, node: NodeType, port_id: str):
        """
        Create a port on a node.

        Args:
            port_id: Unique identifier for this port (unique within the node)
        """
        super().__init__("div")
        self._node = node
        self.port_id = port_id
        self._props["data-port-id"] = port_id
        self.classes("node-port")

        with self:
            self._build()

    @property
    def node(self) -> NodeType:
        return self._node

    def _build(self):
        ui.element().classes(
            "w-[1em] h-[1em] rounded-full bg-orange-500 cursor-pointer"
        )
