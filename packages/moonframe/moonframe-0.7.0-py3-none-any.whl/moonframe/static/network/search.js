import { AppState } from "./global.js"
import { onMouseEnter, onMouseLeave } from "./mouseevent.js"
import { unfocus, setFocus } from "./clickevent.js"

/**
 * Search a node on the graph (with the search bar)
 * @param {event} event 
 * @param {Object} nodes 
 */
export function searchElement(event, nodes) {
    const searchInput = d3.select("#searchInput")
    const searchTerm = searchInput.property("value")
    const tablebody = d3.select("#tablebody")
    const table = d3.select(".table-responsive")
    const focus = d3.select(".focus")
    let matches = nodes.filter(d => d.name.includes(searchTerm))

    if (matches.length !== 0) { // something found

        if (matches.length > 1) { // more than one match -> create a menu
            if (!focus.empty()) {
                unfocus()
            }
            // show the table
            table.attr("hidden", null)

            // not too much matches
            if (matches.length > 10) {
                matches = matches.slice(0, 10)
            }

            // set the table
            matches.forEach(d => {
                const el = d3.select(`[data-id='node-${d.id}']`).node()
                tablebody.append("tr")
                    .append("td")
                    .html(d.path)
                    .attr("class", "tabledata")
                    .on("click", function () {
                        // mock click 
                        setFocus(el, d)
                        // reset table
                        tablebody.selectAll("tr").remove()
                        table.attr("hidden", true)
                        searchInput.property("value", "")
                        // unselect searchInput
                        searchInput.node().blur()
                    })
                    // mock MouseEnter and MouseLeave
                    .on("mouseenter", function () {
                        onMouseEnter.call(el, event, d)
                    })
                    .on("mouseleave", function () {
                        onMouseLeave.call(el)
                    })
            })
        }
        else { // single match
            const el = d3.select(`[data-id='node-${matches[0].id}']`).node()
            if (focus.node() !== el) {
                if (!focus.empty()) {
                    unfocus()
                }
                // mock mouseover => highlight path
                onMouseEnter.call(el, event, matches[0])
                // mock click => select the point
                setFocus(el, matches[0])
            }
        }

    }
    else { // nothign found -> error message
        // placement
        const searchbar = d3.select("#searchbar")
        if (!focus.empty()) {
            unfocus()
        }

        searchbar.append("g")
            .html(`Can't find ${searchTerm}.`)
            .style("color", "red")
            .style("font-size", "small")
            .attr("id", "errorinfo")
        searchInput.attr("class", "form-control is-invalid")
    }
}