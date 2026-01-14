import State from "../utils/state";
import { getCyInstance, debouncedSetValue, debounce } from "../utils/helpers";

// Configs
const DELAYS = {
    default: 150,
    initCollapse: 100,
};

// Module state for tracking collapsed edge groups
let collapsedGroups = {};
let priorityLabel = null;

/**
 * Detects parallel edges in the graph (same source+target pair)
 * Returns a Map where key is "source_target" (sorted) and value is array of edge objects
 */
function detectParallelEdges() {
    const cy = getCyInstance();
    const edgeGroups = new Map();

    cy.edges().forEach((edge) => {
        const source = edge.source().id();
        const target = edge.target().id();
        // Create consistent key regardless of direction by sorting
        const key = [source, target].sort().join("_");

        if (!edgeGroups.has(key)) {
            edgeGroups.set(key, []);
        }
        edgeGroups.get(key).push(edge);
    });

    // Filter to only groups with 2+ edges (parallel edges)
    const parallelGroups = new Map();
    edgeGroups.forEach((edges, key) => {
        if (edges.length > 1) {
            parallelGroups.set(key, edges);
        }
    });

    return parallelGroups;
}

/**
 * Collapses a group of parallel edges into a single meta-edge
 */
function collapseEdgeGroup(groupKey, edges) {
    const cy = getCyInstance();

    // Determine priority edge (first matching priority label, or first edge)
    let priorityEdge = edges[0];
    if (priorityLabel) {
        const matchingEdge = edges.find((e) => e.data("label") === priorityLabel);
        if (matchingEdge) {
            priorityEdge = matchingEdge;
        }
    }

    // Extract computed colors from priority edge before removal
    // This preserves the visual appearance when creating the meta-edge
    const lineColor = priorityEdge.style('line-color');
    const arrowColor = priorityEdge.style('target-arrow-color');

    // Store original edges data before removing
    const originalEdgesData = edges.map((e) => ({
        group: "edges",
        data: { ...e.data() },
    }));

    // Create meta-edge ID
    const metaEdgeId = `_meta_${groupKey}`;

    // Create multi-line label: priority label + count
    const priorityLabelText = priorityEdge.data("label") || "";
    const countText = `(${edges.length})`;
    const metaLabel = priorityLabelText ? `${priorityLabelText}\n${countText}` : countText;

    // Get source/target from first edge (use actual source/target, not sorted)
    const source = edges[0].source().id();
    const target = edges[0].target().id();

    // Remove original edges
    edges.forEach((e) => e.remove());

    // Add meta-edge with special styling marker
    cy.add({
        group: "edges",
        data: {
            id: metaEdgeId,
            source: source,
            target: target,
            label: priorityLabelText,
            _isMetaEdge: true,
            _originalGroupKey: groupKey,
            _edgeCount: edges.length,
            _metaLabel: metaLabel,
            _preservedLineColor: lineColor,
            _preservedArrowColor: arrowColor,
        },
    });

    // Store in collapsed groups state
    collapsedGroups[groupKey] = {
        originalEdges: originalEdgesData,
        metaEdgeId: metaEdgeId,
    };

    State.updateState("collapsedEdges", { ...collapsedGroups });
}

/**
 * Expands a collapsed meta-edge back to original edges
 */
function expandEdgeGroup(groupKey) {
    const cy = getCyInstance();
    const group = collapsedGroups[groupKey];

    if (!group) return;

    // Remove meta-edge
    cy.getElementById(group.metaEdgeId).remove();

    // Restore original edges
    group.originalEdges.forEach((edgeData) => {
        cy.add(edgeData);
    });

    // Remove from collapsed state
    delete collapsedGroups[groupKey];
    State.updateState("collapsedEdges", { ...collapsedGroups });
}

/**
 * Handler for double-click on meta-edge to expand
 */
function _handleExpandEdge(e) {
    const edge = e.target;
    if (edge.data("_isMetaEdge")) {
        const groupKey = edge.data("_originalGroupKey");
        const edgeCount = edge.data("_edgeCount");

        // Send event to Python
        debouncedSetValue({
            action: "expand_edge",
            data: {
                group_key: groupKey,
                edge_count: edgeCount,
            },
            timestamp: Date.now(),
        });

        // Expand the edges
        expandEdgeGroup(groupKey);
    }
}

const edgeActionsHandlers = {
    expand: debounce(_handleExpandEdge, DELAYS.default),
};

/**
 * Collapses all parallel edges in the graph
 */
function collapseAllParallelEdges() {
    const parallelGroups = detectParallelEdges();
    parallelGroups.forEach((edges, groupKey) => {
        collapseEdgeGroup(groupKey, edges);
    });
}

/**
 * Initialize edge actions based on configuration
 */
function initEdgeActions(edgeActions, collapseOnInit, priorityEdgeLabelConfig) {
    priorityLabel = priorityEdgeLabelConfig;

    if (edgeActions.length === 0 && !collapseOnInit) {
        return;
    }

    // Auto-collapse on init if configured
    if (collapseOnInit) {
        // Delay to ensure graph is rendered
        setTimeout(() => {
            collapseAllParallelEdges();
        }, DELAYS.initCollapse);
    }

    // Register double-click handler for expand
    if (edgeActions.includes("expand")) {
        getCyInstance().on(
            "dblclick dbltap",
            "edge[_isMetaEdge]",
            edgeActionsHandlers.expand
        );
    }
}

export { collapseAllParallelEdges, expandEdgeGroup, detectParallelEdges };
export default initEdgeActions;
