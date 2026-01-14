/**
 *  A convex hull is the smalest convex shape enclosing a set of points. 
 *  Because each node is grouped according to its filename, we apply convex hulls to the chart 
 *  to make it easier to identify which nodes belong to the same file. 
 */
import { AppState } from "./global.js"
import { hideTooltip, showTooltip } from "./mouseevent.js"
import { catPalettes } from "../general/palettes.js"
import { updateColorElements } from "./color.js"
/* -------------------------------------------------------------------------- */
/*                                    INIT                                    */
/* -------------------------------------------------------------------------- */

/**
 * Set convex hulls.
 * Each node is grouped according to its filename.
 * @param {Object} nodes data
 */
export function setHulls(nodes) {
    // group nodes
    const groupMap = d3.group(nodes, d => d.filename)

    // create convex hulls
    const hulls = d3.select("#view")
        .selectAll("path")
        .data(groupMap, d => d[0])
        .join("path")
        .attr("class", "hull")
        .style("stroke-width", d => d[1].length > 1 ? 140 : 1)
        .style("stroke-linejoin", "round")
        .style("visibility", "hidden")
        // tooltip
        .attr("data-bs-toggle", "tooltip")
        .attr("data-bs-title", d => d[0])
        .attr("data-bs-trigger", "manual")
        .attr("data-bs-custom-class", "custom-tooltip")
        // events
        .on("mouseenter", function (_, d) {
            const isNotFocus = d3.select(".focus").empty()
            if (isNotFocus && !AppState.isItADrag) {
                highlightHull(d[0])
                addHullTooltip.call(this)
            }
        })
        .on("mouseleave", function (event, d) {
            const isNotFocus = d3.select(".focus").empty()
            if (isNotFocus && !AppState.isItADrag) {
                removeHighlightHull(this, event, d)
                removeHullTooltip.call(this)
            }
        })
}

/**
 * Get convex hull shape.
 * Convex hulls are created with "d3.polygonHull" function but it only works
 * if nb pts in the group >= 3.
 * For : 
 *    - nb pts == 2 : create 2 fake points (very) close to an existing pts to 
 *                    have nb pts > 3
 *    - nb pts == 1 : set a circular shape instead of a convex hull (fake pts 
 *                    technique creates instability when there is only one 
 *                    existing point)
 * 
 * @param {Object} d group data : [{filename (string) : data (Object)}, ...]
 * @returns shape
 */
function groupPath(d) {
    if (d === undefined) {
        return
    }
    let fakePoints = []
    // circular shape = avoid instability 
    if (d.length == 1) {
        const r = 60
        return `M ${d[0].x},${d[0].y - r} 
        A ${r},${r} 0 1,0 ${d[0].x},${d[0].y + r}
        A ${r},${r} 0 1,0 ${d[0].x},${d[0].y - r}
        Z`;
    }
    // convex hulls
    if (d.length == 2) {
        fakePoints = [[d[0].x + 0.001, d[0].y - 0.001],
        [d[0].x - 0.001, d[0].y + 0.001]]
    }
    const points = d.map(i => [i.x, i.y])
        .concat(fakePoints)
        .filter(p => isFinite(p[0]) && isFinite(p[1]))
    const hull = d3.polygonHull(points)
    if (!hull) return null

    return "M" + hull.join("L") + "Z";

}

/* -------------------------------------------------------------------------- */
/*                              UPDATE FUNCTIONS                              */
/* -------------------------------------------------------------------------- */

/**
 * Update convex hull position
 * @param {Object} nodes 
 */
export function updateHulls() {
    const nodes = d3.selectAll('.nodes:not(.hide)').data()
    const groupMap = d3.group(nodes, d => d.filename)

    // update hulls geometry
    const paths = d3.selectAll(".hull")
        .attr("d", d => groupPath(groupMap.get(d[0])))
        .style("stroke-width", d => (groupMap.get(d[0]) && groupMap.get(d[0]).length) > 1 ? 140 : 1)
    // .style("visibility", d => groupMap.get(d[0]) ? "visible" : "hidden")
}

/**
 * Update convex hull colors
 */
export function updateHullsColors(colorPalette) {
    const nodes = d3.selectAll('.nodes').data()
    const domain = [...(new Set(nodes.map(d => d.filename)))]
    let range = catPalettes[colorPalette["cat"]]

    if (colorPalette["cat"] === "Colorblind-safe") {
        const coldomain = Object.keys(range)
        range = Array.from({ length: domain.length }, (_, i) => coldomain[i % coldomain.length])
    }

    // updates color
    const hullColor = d3.scaleOrdinal()
        .domain(domain)
        .range(range.map(c => d3.interpolateRgb(c, "white")(0.5)))
        
        // update hulls
        d3.selectAll(".hull")
        .style("fill", d => hullColor(d[0]))
        .style("stroke", d => hullColor(d[0]))
        
    // update nodes
    const nodeColor = d3.scaleOrdinal()
        .domain(domain)
        .range(range)
    nodes.forEach(function (el) {
        el.color = nodeColor(el["filename"])
    })
    updateColorElements()
}

/**
 * Show convex hulls
 */
export function showHulls(colorPalette) {
    const focus = d3.select(".focus")
    updateHullsColors(colorPalette)
    updateHulls()
    resetHulls()
    if (!focus.empty()) {
        const filename = focus.datum().filename
        highlightHull(filename)
    }
}

/* -------------------------------------------------------------------------- */
/*                                   EVENTS                                   */
/* -------------------------------------------------------------------------- */


/**
 * Highlight a convex hull
 * performance hack : use opacity mask
 * so order must be set correctly : 
 * (g) view
 * ├── (path) highlighted nodes 
 * ├── (line) highlighted links
 * ├── (path) the convex hull of highlighted elements
 * ├── (rect) main opacity mask (visible)
 * ├── (path) others nodes
 * ├── (line) others links
 * └── (path) others convex hulls
 * 
 * @param {string} refname filename on focus
 */
export function highlightHull(refname) {
    // set focusHull
    d3.selectAll(".hull").classed("focusHull", dat => dat[0] === refname ? true : false)
    // set opacity links & nodes that are not in the hull
    d3.selectAll(".linkline").classed("linkInHull", el => (el.target.filename === refname && el.source.filename === refname) ? true : false)
    d3.selectAll(".nodes").classed("selectInHull", el => el.filename === refname ? true : false)
    // hulls are hidden
    // set order
    d3.select(".fade-mask").raise().style("visibility", "visible")
    d3.select(".focusHull").raise()
    d3.selectAll(".linkInHull").raise()
    d3.selectAll(".selectInHull, .flag").raise()
}

/**
 * Removes highlight of a convex hull (is called at "mouseleave")
 * @param {event} event mouseleave event
 * @param {object} d convex hull data
 */
export function removeHighlightHull(thisHull, event, d) {
    const focus = d3.select(".focus").node()
    // skip mouseLeave if a node in the convex hull is focused
    const hullsNodes = getAllNodesInHull(d[0])
    if (!hullsNodes.includes(event.relatedTarget)
        && !hullsNodes.includes(focus)) {
        d3.select(".fade-mask").style("visibility", "hidden")
        resetHulls()
    }
}

/**
 * Reset recuring convex hulls modification
 */
export function resetHulls() {
    d3.selectAll(".hull")
        .style("visibility", "visible")
        .lower()
        .classed("focusHull", false)
    d3.selectAll(".nodes").classed("selectInHull", false)
    d3.selectAll(".linkline").classed("linkInHull", false)
}


/**
 * Get all nodes contained in a convex hull
 * @param {string} filename 
 * @returns array, all nodes contained in a convex hull
 */
function getAllNodesInHull(filename) {
    let hullsNodes = []
    d3.selectAll(".nodes").each(function (el) {
        if (el.filename === filename) {
            hullsNodes.push(this)
        }
    })
    return hullsNodes
}

/* -------------------------------------------------------------------------- */
/*                                   TOOLTIP                                  */
/* -------------------------------------------------------------------------- */

/**
 * Set tooltip for convex hull
 * @param {*} color 
 */
function addHullTooltip() {
    const color = this.style.fill
    showTooltip(this, color)
}

/**
 * Hide tooltip for convex hull
 */
function removeHullTooltip() {
    hideTooltip(this)

}
