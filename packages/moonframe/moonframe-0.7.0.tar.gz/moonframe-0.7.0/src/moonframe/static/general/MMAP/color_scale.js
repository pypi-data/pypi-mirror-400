import { colorLegendCont } from "../color_legend_cont.js"
import { colorLegendCat } from "../color_legend_cat.js"
import { palettes, catPalettes } from "../palettes.js"

/**
 * MMAP common function
 * Create a color legend for a given key and domain. 
 * Distinguish between categorical/continuous and linear/log scales.
 * @param {Array} domain domain of the color scale
 * @param {string} cKey key chosen for the color scale
 * @param {boolean} isLog log scale (True) or not (False)
 * @param {Object} colorRules custom color strategy defined like { pattern : color }
 * @param {Object} colorPalette color palette choice : {"cat" : ..., "cont" : ...}
 * @returns color scale
 */
export function createColorScale(domain, cKey, isLog, colorRules, colorPalette) {
    const log10 = d3.select("#log10_checkbox")
    const legend = d3.select("#legend")
    let color

    if (cKey !== "custom") {
        // continuous scale
        if (domain.every(item => typeof item === "number")) {
            legend.attr("type", "cont")

            log10.attr("disabled", undefined)
            const [min, max] = d3.extent(domain)
            const range = palettes[colorPalette["cont"]]

            if (isLog) { // log
                color = d3.scaleSequentialLog(
                    [1, max]
                    , range)
            }
            else { // linear
                color = d3.scaleSequential([min, max], range)
            }

            colorLegendCont({ color: color })
        }

        // categorical scale
        else {
            legend.attr("type", "cat")
            log10.attr("disabled", true)
            let range = catPalettes[colorPalette["cat"]]

            if (colorPalette["cat"] === "Colorblind-safe") {
                const coldomain = Object.keys(range)
                range = Array.from({ length: domain.length }, (_, i) => coldomain[i % coldomain.length])
            }

            color = d3.scaleOrdinal()
                .domain(domain)
                .range(range)

            colorLegendCat(domain, color)

        }

    }
    // custom color scheme
    else {
        const domain = Object.keys(colorRules)
        const range = [...Object.values(colorRules), "grey"]
        log10.attr("disabled", true)

        color = d3.scaleOrdinal()
            .domain([...domain, "undefined"])
            .range(range)

        colorLegendCat(domain, color)
    }

    return color


}