import { setOrbitingCircles } from "./clickevent.js"
import { setArrow } from "./main.js"

/* -------------------------------------------------------------------------- */
/*                            SCALE INIT FUNCTIONS                            */
/* -------------------------------------------------------------------------- */

/**
 * Create a size scale
 * @param {Object} nodes 
 * @returns shift value
 */
export function createSizeScale(nodes, sKey) {
    const domain = [...(new Set(nodes.map(d => d[sKey])))]

    // Use sqrt scale for the size but some domain goes under 0. 
    // so create a shift
    const [min, max] = d3.extent(domain)
    const size = d3.scaleSqrt()
        .domain([min, max])
        .range([500, 5000])

    nodes.forEach(function (el) {
        el.size = size(el[sKey])
    })
}

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */


/**
 * Updates all size-dependent elements.
 * Is called at the "change" event of sselector.
 * @param {Object} nodes
 * @param {Object} targets list of nodes (id) that are targets
 * @param {Object} sources list of nodes (id) that are sources
 */
export function changeSize(nodes, targets, sources, sKey) {
    const svg = d3.select("#svg")
    const symbol = d3.symbol()
    const shift = createSizeScale(nodes, sKey)
    const focus = d3.select(".focus")

    // update lines
    svg.selectAll(".linkline")
        .attr("marker-end", (d, i) => setArrow(d.source.color, d.target.size, i))

    // update nodes
    svg.selectAll(".nodes")
        .attr("d", d => {
            if (!targets.has(d.id)) return symbol.type(d3.symbolStar).size(d.size)()
            if (!sources.has(d.id)) return symbol.type(d3.symbolSquare).size(d.size)()
            return symbol.type(d3.symbolCircle).size(d.size)() // default
        })

    // update flag
    svg.selectAll(".flag").each(function (d) {
        const circle = d3.select(`#circle-flag-${d.index}`)
            .attr("r", Math.sqrt(d.size + 2))
    })

    // update orbiting circles 
    if (!focus.empty()) {
        const data = focus.datum()
        setOrbitingCircles(data)
    }


}