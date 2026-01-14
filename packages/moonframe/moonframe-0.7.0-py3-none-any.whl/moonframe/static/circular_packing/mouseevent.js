import { adjustColorConstrast_BW } from "../general/MMAP/color_constrast.js"

/**       
 * Run actions on `mouseenter` event : 
 *     - double stroke width
 *     - show tooltip
 * 
 * @param {Event} event Mouseon event.
 * @param {Object} d hovered circle’s data
 */
export function onMouseEnter(event, d) {
    const hover = d3.select(`#circle-${d.index}`)

    // double stroke width
    hover.transition()
        .duration(300)
        .attr("stroke", d => d.children ? d.color : "black")
        .attr("stroke-width", 2)

    // show tooltip
    const tooltip = new bootstrap.Tooltip(hover.node(), {
        placement: 'top'
    })
    tooltip.show()
    tooltip.tip.style.setProperty("--bs-tooltip-bg", d.color)
    tooltip.tip.style.setProperty("--bs-tooltip-color", adjustColorConstrast_BW(d.color, "white"))
}

/**
 * Run actions on `mouseleave` event :  
 *     - reset stroke
 *     - delete all tooltips (safest way to hide it)
 * 
 * @param {Event} event Mouseout event.
 * @param {Object} d hovered circle’s data
 */
export function onMouseLeave(event, d) {
    const hover = d3.select(`#circle-${d.index}`)

    // reset stroke
    hover.transition()
        .duration(300)
        .attr("stroke", d => d.children ? d.color : "null")
        .attr("stroke-width", 1)

    // delete all tooltips 
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        const tip = bootstrap.Tooltip.getInstance(el);
        if (tip) tip.dispose()
    })
}
