// zoom

import { showCard } from "../general/MMAP/card.js"

let view

/**
 * Set the zoom simulation
 * @param {Object} d focus circle's data
 */
export function zoom(d, isCard = true) {
    d3.selectAll(".pulse").remove()
    const focus = d3.select(`#circle-${d.index}`)
    const zI = d3.select("#zoom-input")
    // slider reversed (see main.rebootView())
    const zoomValue = zI.property("max") - (zI.property("value") - zI.property("min"))

    // if the zoom is already focused on the circle : do nothing
    if (!focus.classed("focus")) {
        const svg = d3.select("#view")
        const zoomfactor = (!d.children) ? zoomValue * 2 : zoomValue

        d3.selectAll(".circle").classed("focus", false)
            .filter(el => el !== d && !el.children)
            .attr("stroke", "null")

        focus.classed("focus", true)

        if (isCard) {
            if (d.index !== 0) {
                showCard(d.data, d.color)
            }
            else {
                d3.select("#card").attr("hidden", true)
            }
        }


        const parent = d.parent ?? d
        // for performance reasons, update only the paths for the parent's descendants
        const include = parent.descendants().map(el => el.index)

        const transition = svg.transition()
            .duration(750)
            .tween("zoom", z => {
                const i = d3.interpolateZoom(view, [d.x, d.y, d.r * zoomfactor])
                return t => zoomTo(i(t), include)
            })

        transition.on("end", function () {
            if (isCard) {
                if (d.index !== 0) {
                    d3.select("#view")
                        .append("circle")
                        .attr("cx", 0)
                        .attr("cy", 0)
                        .attr("r", window.innerHeight / zoomfactor)
                        .attr("class", "pulse")
                        .style("stroke", d.color)
                        .style("fill", "none")
                }
            }
        })
    }
}


/**
 * Zoom in/out : 
 * update all svg elements according to the new view coordinates
 * @param {Array} v New view coordinates [x,y,r] 
 * @param {Array} include list of `circle-path` to update. 
 * Otherwise, applying it to all circle-paths can be costly.
 */
export function zoomTo(v, include = []) {
    const k = window.innerHeight / v[2]
    const circle = d3.selectAll(".circle")
    const path = d3.selectAll(".circlePath")
    const text = d3.selectAll("textPath")

    view = v

    const zoomCoords = (d, v, k) => ({
        cx: (d.x - v[0]) * k,
        cy: (d.y - v[1]) * k,
        r: d.r * k
    })

    // update circles
    circle
        .attr("transform", d => {
            const { cx, cy } = zoomCoords(d, v, k)
            return `translate(${cx},${cy})`
        })
        .attr("r", d => d.r * k)

    // update circular text
    path
        .filter(d => include.includes(d.index))
        .attr("d", function (d) {
            const { cx, cy, r } = zoomCoords(d, v, k)
            return `M ${cx} ${cy + r}
                        A ${r} ${r} 0 1 1 ${cx} ${cy - r}
                        A ${r} ${r} 0 1 1 ${cx} ${cy + r}`
        })
    text.attr("visibility", function (d) {
        if (include.includes(d.index)) {
            if (d3.select(this).node().parentNode.getComputedTextLength() >= (2 * Math.PI * d.r * k) * 0.6
                || text.node().getBBox().height > d.r * k) {
                return "hidden"
            }
            else { return "visible" }
        }
        else {
            return "hidden"
        }

    })

    // update tooltip (handle by Bootstrap)
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        const tip = bootstrap.Tooltip.getInstance(el);
        if (tip) tip.update()
    })

}