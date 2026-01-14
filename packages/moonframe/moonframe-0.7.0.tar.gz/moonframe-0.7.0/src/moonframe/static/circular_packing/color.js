import { updateCardColors } from "../general/MMAP/card.js"
import { createColorScale } from "../general/MMAP/color_scale.js"

/**
 * Set the color variable for each element in tree (=> d.color)
 * @param {Object} tree tree's data
 * @param {String} cKey color key
 * @param {Boolean} isLog Log scale (true) or not (false)
 * @param {Object} colorRules (optional) custom color scale 
 * @param {Object} colorPalette color palette choice : {"cat" : ..., "cont" : ...}
 */
export function setColor(tree, cKey, isLog, colorRules, colorPalette) {
    const domain = [... (new Set(tree.descendants().map(d => d.data[cKey])))]
    const color = createColorScale(domain, cKey, isLog, colorRules, colorPalette)
    tree.each(function (el) {
        el.color = color(el.data[cKey])
    })
}

/**
 * Update color at change
 * @param { Object } tree tree's data
 * @param { String } cKey color key
 * @param { Boolean } isLog log scale (true) or not (false)
 * @param { Object } colorRules (optional) custom color scale
 * @param {Object} colorPalette color palette choice : {"cat" : ..., "cont" : ...}
 */
export function changeColor(tree, cKey, isLog, colorRules, colorPalette) {
    // reset
    d3.select("#legend").selectAll("*").remove()
    const focus = d3.select(".focus").datum()
    setColor(tree, cKey, isLog, colorRules, colorPalette)

    const rootColor = d3.color(tree.color).copy({ opacity: 0.2 })
    document.documentElement.style.setProperty('--root-color', rootColor)


    // update circles
    d3.selectAll(".circle")
        .attr("fill", d => d.children ? d3.interpolateRgb(d.color, "white")(0.7) : d.color)
        .attr("stroke", d => d.children ? d.color : "null")
        .each((d) => d3.select(`#circleText-${d.index}`).style("fill", d.color))
        .attr("data-bs-title", d => `<b>${d.name}</b><br>${d.data[cKey]}`)

    d3.select(".pulse").style("stroke", focus.color)

    // update card
    updateCardColors()


}

