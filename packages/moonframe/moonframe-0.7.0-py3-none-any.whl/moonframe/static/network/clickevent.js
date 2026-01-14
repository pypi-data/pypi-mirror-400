
import { AppState } from "./global.js"
import { showTooltip, clearPathHighlight, hideTooltip, onMouseEnter } from "./mouseevent.js"
import { resetHulls } from "./hulls.js"
import { showCard } from "../general/MMAP/card.js"

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */

/**
 * Focus/unfocus any node
 * @param {Object} el node (dom)
 * @param {Object} d  data
 */
export function selectPoint(el, d) {
    const focus = d3.select(".focus")
    // unfocus
    if (focus.node() === el) {
        focus.classed("focus", false)
        d3.select(".orbit-group").selectAll("*").remove()
    }
    // focus
    else {
        setFocus(el, d)
    }

}

/* -------------------------------------------------------------------------- */
/*                           FOCUS/ONFOCUS FUNCTIONS                          */
/* -------------------------------------------------------------------------- */

/**
 * Cleaner way to focus a point
 * @param {Object} el node
 * @param {Object} d data
 */
export function setFocus(el, d) {
    const focus = d3.select(".focus")
    // there is a previous point
    if (!focus.empty()) {
        // unselect the previous point
        unfocus()
        // mock mouseenter
        onMouseEnter.call(el, undefined, d)
    }
    d3.select(el).classed("focus", true)
    document.documentElement.style.setProperty('--focus-color', d.color)
    showCard(d, d.color)
    showTooltip(el, d.color)
    setOrbitingCircles(d)
}

/**
 *  Cleaner way to unfocus a point
 */
export function unfocus() {
    const focus = d3.select(".focus")
    hideTooltip(focus.node())
    focus.classed("focus", false)
    clearPathHighlight()
    d3.select(".orbit-group").selectAll("*").remove()
    if (AppState.isHullVisible) {
        resetHulls()
    }
}

/* -------------------------------------------------------------------------- */
/*                              ORBITING CIRCLES                              */
/* -------------------------------------------------------------------------- */

/**
 * Set orbiting circles around the focus point.
 * @param {Object} d Data of the node on focus
 */
export function setOrbitingCircles(d) {
    d3.select(".orbit-group").selectAll("*").remove()
    const mainRadius = Math.sqrt(d.size) + 2
    const radius = Math.sqrt(d.size) / 10
    // 1/3
    const dotCount = Math.trunc(2 * Math.PI * mainRadius / radius / 3)
    // style
    const color = AppState.isHullVisible ? "white" : d.color
    const stroke = AppState.isHullVisible ? d.color : "white"

    for (let i = 0; i < dotCount; i++) {
        const angle = (2 * Math.PI * i) / dotCount
        d3.select(".orbit-group")
            .append("circle")
            .attr("class", "orbit-dot")
            .attr("cx", Math.cos(angle) * mainRadius)
            .attr("cy", Math.sin(angle) * mainRadius)
            .attr("r", radius)
            .style("stroke", "white")
            .style("stroke-width", "1px")
            .attr("opacity", "0.8")
            .style("fill", d.color)
        d3.select(".orbit-container").attr("transform", `translate(${d.x},${d.y})`)
    }
}