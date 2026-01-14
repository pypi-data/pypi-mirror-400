"""Reactflow Profile Entity. This entity is used to store the profile of the reactflow."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Edge(BaseModel):
    """Edge Entity. This entity is used to store the edge of the reactflow."""

    source: str | None = None
    sourceHandle: str | None = None
    target: str | None = None
    targetHandle: str | None = None
    strokeWidth: int = 2
    animated: bool = False
    type: str | None = None
    id: str | None = None
    selected: bool = False


class Viewport(BaseModel):
    """Viewport Entity. This entity is used to store the viewport of the reactflow."""

    x: float
    y: float
    zoom: float


# Node definition
# ------------------------------------------------------------
class Position(BaseModel):
    """Position Entity. This entity is used to store the position of the node."""

    x: float
    y: float


class Measured(BaseModel):
    """Measured Entity. This entity is used to store the measured of the node."""

    width: int
    height: int


class BaseNode(BaseModel):
    """BaseNode Entity. This entity is used to store the node of the reactflow.

    This is the base class for all nodes.
    """

    id: str | None = None
    position: Position | None = None
    measured: Measured | None = None
    style: Measured | None = None
    selected: bool = False
    draggable: bool = True
    focusable: bool = True
    selectable: bool = True
    dragging: bool = False
    root_node: bool = False
    # NOTE: Following fields should be defined in the subclass
    # type: NodeType | None = None
    # data: BackendServerNodeData | McpServerNodeData | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )


# Flow definition
# ------------------------------------------------------------
class BaseFlow(BaseModel):
    """BaseFlow Entity. This entity is used to store the flow of the reactflow.

    This is the base class for all flows.
    """

    edges: list[Edge] | None = None
    viewport: Viewport | None = None
    # NOTE: Following fields should be defined in the subclass
    # nodes: list[BaseNode] | None = None
