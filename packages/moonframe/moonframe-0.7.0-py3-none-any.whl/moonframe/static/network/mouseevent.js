import { adjustColorConstrast_BW } from "../general/MMAP/color_constrast.js"
import { AppState } from "./global.js"
import { highlightHull } from "./hulls.js"

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */

/**
 * Event "mouseenter"
 * @param {event} event 
 * @param {Object} d data
 */
export function onMouseEnter(event, d) {
    const focus = d3.select(".focus")
    const hover = d3.selectAll(".hover")

    // bugfix : sometimes miss "mouseLeave"
    if (!hover.empty()) {
        hover.each(function (el) {
            if (el !== d) {
                onMouseLeave.call(this)
            }
        })

    }

    // MouseEnter event only if there isn't a focus point or the select node
    // is part of the focus point path.
    // && it was indeed a mouseEnter not a drag (isItADrag?)
    if (focus.empty()
        || d3.select(this).classed("selectInPath") === true
        || d3.select(this).classed("selectInHull") === true
        && !AppState.isItADrag) {

        d3.select(this).classed("hover", true)

        if (d3.select(this).classed("flag") === false) {
            showTooltip(this, d.color)
        }
        // if there isn't a focus point -> calls highlightPath
        // else, keep the path of the focus point (= change nothing)
        if (focus.empty()) {
            AppState.hoverTimeout = setTimeout(function () {
                if (AppState.isHullVisible) {
                    const focusHull = d3.select(".focusHull")
                    const hullID = focusHull.empty() ? null : focusHull.datum()[0]
                    if (hullID !== d.filename) {
                        highlightHull(d.filename)
                    }
                }
                highlightPath(d.id)
            }, 500)
        }

        const currentTheme = document.documentElement.getAttribute('data-bs-theme')
        d3.select(this).style("stroke", currentTheme === "light" ? "black" : "white")
        document.documentElement.style.setProperty('--hover-color', d.color)
    }
}

/**
 *  Event "mouseleave":
 *      - hide the tooltip
 *      - remove the stroke
 *      - clear the path 
 */
export function onMouseLeave() {
    const focus = d3.select(".focus")
    const point = d3.select(this)

    // clear the path only if there is no selection
    if (focus.empty()) {
        clearPathHighlight()
    }
    else {
        point.style("stroke", null)
    }
    if (this !== focus.node() && !this.classList.contains("flag")) {
        hideTooltip(this)
    }
    point.classed("hover", false)

}

/* -------------------------------------------------------------------------- */
/*                               PATH FUNCTIONS                               */
/* -------------------------------------------------------------------------- */

/**
 *  Highlight the "path" of a node :
 *  -> get all possible targets starting from this node
 *  -> get closest sources
 * 
 * performance hack : use opacity mask
 * so order must be set correctly : 
 * (g) view
 * ├── (path) highlighted nodes 
 * ├── (line) highlighted links
 * ├── (path) the convex hull of highlighted elements (visible or not)
 * ├── (rect) main opacity mask (visible)
 * ├── (path) others nodes
 * ├── (line) others links
 * └── (path) others convex hulls (visible or not)
 * 
 *  @param {int} id index of the node
 */
export function highlightPath(id) {

    highlightLinksTarget(id)
    highlightLinksSource(id)

    d3.select(".fade-mask").raise().style("visibility", "visible")
    if (AppState.isHullVisible) {
        d3.selectAll(".focusHull").raise()
    }
    d3.selectAll(".linkInPath, .linkInHull").raise()
    d3.selectAll(".selectInPath, .selectInHull, .flag").raise()
}

/**
 * [RECURSIVE] Highlight all possible targets starting from a node.
 * @param {int} id index of the node
 */
function highlightLinksTarget(id) {
    d3.select(`[data-id='node-${id}']`).classed("selectInPath", true)
    const sources = d3.selectAll(".linkline").filter(l => l.source.id === id)
    sources.each(function (l) {
        // ignore recursive function, hidden links & pts
        if (l.target.id !== id && !d3.select(this).classed("hide")) {
            d3.select(this).classed("linkInPath", true)
            if (d3.select(`[data-id='node-${l.target.id}']`).classed("selectInPath") !== true) {
                highlightLinksTarget(l.target.id)
            }
        }

    }
    )
}


/**
 * Highlight closest sources from a node.
 * @param {int} id index of the node
 */
function highlightLinksSource(id) {
    d3.select(`[data-id='node-${id}']`).classed("selectInPath", true)
    const targets = d3.selectAll(".linkline").filter(l => l.target.id === id)
    targets.each(function (l) {
        // ignore hidden links & pts
        if (!d3.select(this).classed("hide")) {
            d3.select(this).classed("linkInPath", true)
            d3.select(`[data-id='node-${l.source.id}']`).classed("selectInPath", true)
        }
    }
    )
}


/**
 *  Clear any "path" (see HighlightPath function)
 */
export function clearPathHighlight() {
    clearTimeout(AppState.hoverTimeout)
    d3.selectAll(".linkline").classed("linkInPath", false).lower()
    d3.select("#card").attr("hidden", true)
    d3.select(".fade-mask").style("visibility", "hidden")
    d3.selectAll(".nodes")
        .classed("selectInPath", false)
        .style("stroke", "white")
    d3.selectAll(".linkline").classed("linkInPath", false)
}

/* -------------------------------------------------------------------------- */
/*                              TOOLTIP FUNCTION                              */
/* -------------------------------------------------------------------------- */

/**
 * Show a node's tooltip.
 * @param {Object} el node (dom)
 * @param {String} color background color of the tooltip
 */
export function showTooltip(el, color = "black") {
    let tooltip = bootstrap.Tooltip.getInstance(el)
    if (tooltip) {
        tooltip.update()
    }
    else {
        tooltip = new bootstrap.Tooltip(el)
        tooltip.show()
    }
    setTooltipColor(tooltip, color)
}

/**
 * Hide (or rather delete) a node's tooltip.
 * @param {Object} el node (dom)
 */
export function hideTooltip(el) {
    const tooltip = bootstrap.Tooltip.getInstance(el)
    if (tooltip) {
        tooltip.dispose()
    }

}

/**
 * Update pos tooltip
 * @param {Object} el node (dom)
 */
export function updateTooltip(el) {
    const tooltip = bootstrap.Tooltip.getInstance(el)
    if (tooltip) {
        tooltip.update()
    }
}


/**
 * Set tooltip's background color
 * @param {Object} tooltip tooltip
 * @param {String} color background color
 */
export function setTooltipColor(tooltip, color) {
    tooltip.tip.style.setProperty("--bs-tooltip-bg", color)
    tooltip.tip.style.setProperty("--bs-tooltip-color", adjustColorConstrast_BW(color, "white"))
}
