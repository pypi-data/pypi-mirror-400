import { updateCardColors } from "../general/MMAP/card.js"
import { adjustColorContrast } from "../general/MMAP/color_constrast.js"
import { createColorScale } from "../general/MMAP/color_scale.js"
import { setArrow } from "./main.js"
import { setTooltipColor } from "./mouseevent.js"

/* -------------------------------------------------------------------------- */
/*                               SCALE FUNCTIONS                              */
/* -------------------------------------------------------------------------- */

export function setColor(nodes, cKey, isLog, colorRules, colorPalette = { "cat": "Observable10", "cont": "plasma" }) {
    const domain = [... (new Set(nodes.map(d => d[cKey])))]
    const color = createColorScale(domain,
        cKey,
        isLog,
        colorRules,
        colorPalette)

    nodes.forEach(function (el) {
        el.color = color(el[cKey])
    })
}

/**
 * Updates all color-dependant elements after modification of nodes' color
 * Is called at the "change" event of cselector.
 */
export function updateColorElements() {
    // update svg elements
    d3.selectAll(".nodes").attr("fill", d => d.color)
        .style("--fill-color", d => d.color)
    d3.selectAll(".linkline")
        .attr("stroke", d => d.source.color)
        .attr("marker-end", (d, i) => setArrow(d.source.color, d.target.size, i))

    d3.selectAll(".flag, .hover, .focus").each(function (d) {
        // change color tooltip
        const tooltip = bootstrap.Tooltip.getInstance(this)
        setTooltipColor(tooltip, d.color)

        // update orbit-group
        if (this.classList.contains("focus")) {
            d3.select(".orbit-group")
                .selectAll("circle")
                .style("fill", d.color)
            // glowing effect 
            document.documentElement.style.setProperty('--focus-color', d.color)
        }

        // update circle-flag
        if (this.classList.contains("flag")) {
            const themeColor = document.documentElement.getAttribute('data-bs-theme')
            const bg = themeColor === "light" ? "white" : "black"
            const colorFlag = adjustColorContrast(bg, d.color)
            const circle = d3.select(`#circle-flag-${d.index}`)
                .style("fill", colorFlag)
                .style("stroke", colorFlag)
        }
    })

    updateCardColors()

}

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTIONS                              */
/* -------------------------------------------------------------------------- */

/**
 * Event change of color 
 *  -> create the new color scale and update all color-dependant elements
 * @param {Object} nodes 
 */
export function changeColor(nodes, cKey, isLog, color_rules, colorPalette) {
    d3.select("#legend").selectAll("*").remove()

    setColor(nodes, cKey, isLog, color_rules, colorPalette)
    updateColorElements()
}

