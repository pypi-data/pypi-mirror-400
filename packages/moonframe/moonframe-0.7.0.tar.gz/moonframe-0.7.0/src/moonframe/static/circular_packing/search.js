import { onMouseEnter, onMouseLeave } from "./mouseevent.js"
import { zoom } from "./zoom.js"

/**
* Search an element by name from search bar input
* Display only the 10 closest names
* @param { Event } event keyup event (on searchInput)
* @param { Object } tree tree's data
*/
export function searchElement(event, tree, isCard) {
    const searchInput = d3.select("#searchInput")
    const searchTerm = searchInput.property("value")
    const tablebody = d3.select("#tablebody")
    const table = d3.select(".table-responsive")
    const sKey = tree.data.sKey

    // search closest match
    let matches = tree.descendants().filter(d => d.name.includes(searchTerm) && d.data[sKey] > 0)

    if (matches.length !== 0) { // something found

        // show the table
        table.attr("hidden", null)

        // not too much matches
        if (matches.length > 10) {
            matches = matches.slice(0, 10)
        }

        // set the table
        matches.forEach(d => {
            tablebody.append("tr")
                .append("td")
                .html(d.name)
                .attr("class", "tabledata")
                .on("click", function () {
                    // mock leave mouse bc it isn't a natural "click" i.e. 
                    // cursor not actually in circle so it never detects
                    // mouseLeave
                    onMouseLeave(event, d)
                    // mock click 
                    zoom(d, isCard)
                    // reset table
                    tablebody.selectAll("tr").remove()
                    table.attr("hidden", true)
                    searchInput.property("value", "")
                    // unselect searchInput
                    searchInput.node().blur()
                })
                // mock MouseEnter and MouseLeave
                .on("mouseenter", function () {
                    onMouseEnter(event, d)
                })
                .on("mouseleave", function () {
                    onMouseLeave(event, d)
                })
        })
    }

    else { // nothign found -> error message
        // placement
        const searchbar = d3.select("#searchbar")

        searchbar.append("g")
            .html(`Can't find ${searchTerm}.`)
            .attr("id", "errorinfo")
        searchInput.attr("class", "form-control is-invalid")
    }
}

