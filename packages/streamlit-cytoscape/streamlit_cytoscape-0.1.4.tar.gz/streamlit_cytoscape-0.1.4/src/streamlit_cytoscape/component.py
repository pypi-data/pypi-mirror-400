import os
import streamlit.components.v1 as components
from typing import Optional, Union, Callable, Literal, Dict, Any, List

from streamlit_cytoscape.layouts import LAYOUTS
from streamlit_cytoscape.styles import NodeStyle, EdgeStyle
from streamlit_cytoscape.events import Event


_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_cytoscape",
        url="http://localhost:3001",  # For development
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "streamlit_cytoscape",
        path=build_dir,  # For distribution
    )


def streamlit_cytoscape(
    elements: Dict[str, Any],
    layout: Union[str, Dict[str, Any]] = "cose",
    node_styles: List[NodeStyle] = [],
    edge_styles: List[EdgeStyle] = [],
    height: int = 500,
    key: Optional[str] = None,
    on_change: Optional[Callable[..., None]] = None,
    node_actions: List[Literal["remove", "expand"]] = [],
    edge_actions: List[Literal["collapse", "expand"]] = [],
    collapse_parallel_edges: bool = False,
    priority_edge_label: Optional[str] = None,
    meta_edge_style: Optional[Dict[str, Any]] = None,
    events: List[Event] = [],
    hide_underscore_attrs: bool = True,
) -> Any:
    """
    Renders a link analysis graph using Cytoscape in Streamlit.

    Parameters
    ----------
    elements : dict
        Graph elements data including nodes and edges. Each node
        should have an 'id', and 'label'. Each edge should have
        an 'id', 'source', 'target', and 'label'.
    layout : Union[str, dict], default 'cose'
        Layout configuration for Cytoscape. If a string is
        provided, it specifies the layout name. If a dictionary
        is provided, it should contain layout options. Default is
        "cose". A list of support layouts and default settings is
        available in `streamlit_cytoscape.layouts`
    node_styles : list[NodeStyle], default []
        A list of custom NodeStyle instances to apply styles to
        node groups in the graph
    edge_styles : list[EdgeStyle], default []
        A list of custom EdgeStyle instances to apply styles to
        edge groups in the graph
    height: int, default 500
        Component's height in pixels. NOTE: only defined once.
        Changing the value requires remounting the component.
    key : str, default None
        A unique key for the component. If provided, this key
        allows multiple instances of the component to exist in
        the same Streamlit app without conflicts. Setting this
        parameter is also important to avoid unnecessary
        re-rendering of the component.
    node_actions: list[Literal['remove', 'expand']], default []
        Specifies the actions to enable for nodes. Valid options
        are 'remove' and 'expand'. 'remove' allows nodes to be
        removed via delete keydown or a remove button click.
        'expand' allows nodes to be expanded via double-click or
        an expand button click. When any of these actions are
        triggered, the event information is sent back to the
        Streamlit app as the component's return value. CAUTION:
        keeping an edge with missing source or target IDs will
        lead to an error.
    edge_actions: list[Literal['collapse', 'expand']], default []
        Specifies the actions to enable for edges. Valid options
        are 'collapse' and 'expand'. When enabled, parallel edges
        (multiple edges between the same source and target nodes)
        can be collapsed into a single meta-edge showing a priority
        label and count. 'expand' allows collapsed meta-edges to be
        expanded via double-click, restoring the original edges.
    collapse_parallel_edges: bool, default False
        If True, parallel edges will be automatically collapsed
        into meta-edges on initial render. Requires edge_actions
        to include 'expand' to allow users to expand them.
    priority_edge_label: Optional[str], default None
        When collapsing parallel edges, specifies which edge label
        should be shown as the priority label on the meta-edge.
        If None or not found, the first edge's label is used.
    meta_edge_style: Optional[Dict[str, Any]], default None
        A dictionary of Cytoscape.js styles to apply to collapsed
        meta-edges. This allows customization of the meta-edge
        appearance (e.g., line-color, width, line-style). For
        available styles, visit: https://js.cytoscape.org/#style
    events: list[Event], default []
        For advanced usage only. A list of events to listen to.
        When any of these events are triggered, the event
        information is sent back to the Streamlit app as the
        component's return value. NOTE: only defined once.
        Changing the list of events requires remounting the
        component.
    hide_underscore_attrs: bool, default True
        If True, element data attributes with keys starting with
        an underscore (_) will be hidden from the infopanel. This
        allows distinguishing between user-facing data and internal
        styling/rendering data.
    """
    node_styles_dump = [n.dump() for n in node_styles]
    edge_styles_dump = [e.dump() for e in edge_styles]
    style = node_styles_dump + edge_styles_dump

    height_str = str(height) + "px"

    if isinstance(layout, str):
        layout_config = LAYOUTS[layout]
    else:
        layout_config = layout

    events_dump = [e.dump() for e in events]

    return _component_func(
        elements=elements,
        style=style,
        layout=layout_config,
        height=height_str,
        key=key,
        on_change=on_change,
        nodeActions=node_actions,
        edgeActions=edge_actions,
        collapseParallelEdges=collapse_parallel_edges,
        priorityEdgeLabel=priority_edge_label,
        metaEdgeStyle=meta_edge_style or {},
        events=events_dump,
        hideUnderscoreAttrs=hide_underscore_attrs,
    )
