/**
 * Create a categorical scale
 * @param {Object} color scale
 * @param {Array} domain list of possible values for the selected metric
 */
export function colorLegendCat(domain, color) {
    const itemHeight = 20
    const legend = d3.select("#legend")
        .attr("height", itemHeight * (domain.length + 1))
        .attr("viewBox", undefined)
        .append("g")

    let row = -1
    domain.forEach((cat, i) => {
        row += 1

        const group = legend.append("g")
            .attr("id", "otherlegend")
            .attr("transform", `translate(0, ${row * itemHeight})`)

        group.append("rect")
            .attr("width", 10)
            .attr("height", 10)
            .attr("fill", color(cat))

        group.append("text")
            .attr("x", 14)
            .attr("y", 9)
            .attr("id", `legend-${i}`)
            .text(cat)
            .style("font-size", "14px")
            .style("fill", "var(--bs-body-color)");
    })

}