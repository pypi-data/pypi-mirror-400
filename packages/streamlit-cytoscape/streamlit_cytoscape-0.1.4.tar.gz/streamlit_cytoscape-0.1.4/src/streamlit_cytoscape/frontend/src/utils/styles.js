// Color theme
const COLOR = {
    dark: {
        highlight: "rgb(210, 0, 0)",
        line: "rgb(48, 49, 57)",
        font: "rgb(250, 250, 250)",
        border: "rgb(48, 49, 57)",
        fontHighlight: "rgb(250, 250, 250)",
    },
    light: {
        line: "rgb(195,195,195)",
        font: "rgb(5,5,5)",
        border: "rgb(250,250,250)",
        highlight: "rgb(255,50,50)",
        fontHighlight: "rgb(250, 250, 250)",
    },
};

// Common style configs
const fixedNodeStyles = {
    "width": 20,
    "height": 20,
    "border-width": 0.8,
    "font-size": 3.6,
    "text-valign": "bottom",
    "text-margin-y": 3.2,
    "background-repeat": "no-repeat",
    "background-width": "60%",
    "background-height": "60%",
    "background-color": "#0a0a0a",
};

const fixedEdgeStyles = {
    "width": 2,
    "font-size": 3.2,
    "text-rotation": "autorotate",
    "text-background-padding": 1,
    "text-background-opacity": 1,
    "text-background-shape": "round-rectangle",
    "arrow-scale": 0.6,
    "curve-style": "bezier",
};

const fixedNodeHStyles = {
    "outline-width": 0.6,
    "font-weight": "bold",
    "text-background-opacity": 1,
    "text-background-shape": "round-rectangle",
    "text-background-padding": 1,
};

const fixedEdgeHStyles = {
    "font-weight": "bold",
};

const fixedMetaEdgeStyles = {
    "line-style": "dashed",
    "width": 3,
    "text-wrap": "wrap",
    "text-max-width": "100px",
    "text-rotation": 0,
    "font-size": 5,
    "text-halign": "center",
    "text-valign": "center",
};

function _getDefault(theme) {
    return [
        {
            selector: "*",
            style: {
                "min-zoomed-font-size": 10,
            },
        },
        {
            selector: "node",
            style: {
                ...fixedNodeStyles,
                "color": COLOR[theme].font,
                "border-color": COLOR[theme].border,
            },
        },
        {
            selector: "edge",
            style: {
                ...fixedEdgeStyles,
                "color": COLOR[theme].font,
                "line-color": COLOR[theme].line,
                "background-color": COLOR[theme].line,
                "target-arrow-color": COLOR[theme].line,
                "text-background-color": COLOR[theme].line,
            },
        },
    ];
}

// Meta-edge styles need to be applied after custom styles to ensure
// the _metaLabel is used instead of being overridden by edge[label="X"] styles
function _getMetaEdge() {
    return [
        {
            selector: "edge[_isMetaEdge]",
            style: {
                ...fixedMetaEdgeStyles,
                "label": "data(_metaLabel)",
                // Use preserved colors from priority edge to maintain visual consistency
                "line-color": "data(_preservedLineColor)",
                "target-arrow-color": "data(_preservedArrowColor)",
            },
        },
    ];
}

function _getHighlight(theme) {
    return [
        {
            selector: "node:selected, node.highlight",
            style: {
                ...fixedNodeHStyles,
                "color": COLOR[theme].fontHighlight,
                "text-background-color": COLOR[theme].highlight,
                "outline-color": COLOR[theme].highlight,
            },
        },
        {
            selector: "edge:selected, edge.highlight",
            style: {
                ...fixedEdgeHStyles,
                "color": COLOR[theme].fontHighlight,
                "line-color": COLOR[theme].highlight,
                "target-arrow-color": COLOR[theme].highlight,
                "text-background-color": COLOR[theme].highlight,
            },
        },
    ];
}

const STYLES = {
    light: {
        default: _getDefault("light"),
        metaEdge: _getMetaEdge(),
        highlight: _getHighlight("light"),
    },
    dark: {
        default: _getDefault("dark"),
        metaEdge: _getMetaEdge(),
        highlight: _getHighlight("dark"),
    },
};

export default STYLES;
