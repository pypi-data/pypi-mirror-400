import { adjustColorContrast } from "./color_constrast.js"

let cat = {
    "General": [],
    "Size Info": [],
    "Code Metrics": [],
}
const defaultGeneral = ["name", "path", "filename", "type", "lines", "language", "linestart", "comment"]
const defaultSize = ["volume", "assize", "ssize", "ANLOC", "NLOC"]
/**
 * Initialise card by creating the different categories
 * @param {Object} data Root's data
 * @param {Array} exclude list of name to exclude in the data. Default to [].
 * @param {bool} isSummary Include summary in the card (true) or not (false). 
 */
export function initCard(data, exclude, isSummary = false) {
    // set code metrics
    cat["General"] = defaultGeneral.filter(el => !exclude.includes(el))
    cat["Size Info"] = defaultSize.filter(el => !exclude.includes(el))
    const others = [...cat["General"], ...cat["Size Info"], ...exclude]
    cat["Code Metrics"] = Object.keys(data).filter((el) => !others.includes(el))

    d3.select("#accordionCard").style("margin-top", "-14px")

    if (isSummary) {
        cat["Summary"] = []
    }

    Object.entries(cat).forEach(([name, _], index) => {
        createCat(index + 1, name)
    })

}


/**
 * Display element's data in a card
 * @param {Object} d data to display
 * @param {string} color background color of the card header
 */
export function showCard(d, color) {
    const card = d3.select("#card")

    // cats
    Object.entries(cat).forEach(([name, value], index) => {
        if (name !== "Summary") {
            const keys = value.filter(el => Object.keys(d).includes(el))
            setCat(keys, d, index + 1)
        }
        else {
            setSummary(d, index + 1)
        }
    })

    // header
    const cardheader = d3.select("#cardheader")
    cardheader.selectAll("*").remove()
    cardheader
        .append("i")
        .attr("class", function () {
            if (d.type === "folder") {
                return "bi bi-folder-fill card-header-icon me-2"
            }
            else if (d.type === "file") {
                return "bi bi-file-earmark-fill card-header-icon me-2"
            }
            else {
                return "bi bi-box-fill card-header-icon me-2"
            }

        })
        .attr("id", "icon-card-header")
    cardheader.append("h3").html(`${d.name}`)
        .attr("class", "card-header-text mb-0")

    card.attr("hidden", null)

    updateCardColors()
}


/**
 * Create a category in the card
 * @param {Number} index index of the category 
 * @param {String} name name of the cateogry
 */
function createCat(index, name) {
    const accordion = d3.select("#accordionCard")
    const item = accordion.append("div")
        .attr("class", "accordion-item")

    // set text container
    accordion.append("div")
        .attr("class", "accordion-collapse collapse show")
        // .attr("data-bs-parent", "#accordionCard")
        .attr("id", `accordion-collapsed-${index}`)
        .style("margin-top", "10px")
        .append("div")

    // set button property
    const button = item.append("button")
        .attr("class", "accordion-button")
        .attr("type", "button")
        .attr("data-bs-toggle", "collapse")
        .attr("data-bs-target", `#accordion-collapsed-${index}`)
        .attr("aria-controls", `accordion-collapsed-${index}`)
        .attr("aria-expanded", "true")
        .style("display", "flex")
        .style("align-items", "center")

    //icon
    button.append("i")
        .attr("class", `bi bi-${index}-circle-fill button-card`)
        .style("margin-right", "5px")
        .style("font-size", "16px")
    // title
    button.append("div")
        .html(name)
        .attr("id", `button-card-title`)
        .attr("class", "button-card")
}

/**
 * Display all (key,value) pairs of a category in the card as a table.
 * All keys must exist in d (access with d[key]).
 * @param {Array} keys list of keys
 * @param {Object} d data
 * @param {Number} index index of the category
 */
function setCat(keys, d, index) {
    const collapsed = d3.select(`#accordion-collapsed-${index}`)

    // reset
    collapsed.selectAll("*").remove()

    // set data
    for (let k of keys) {
        const row = collapsed.append("div").style("display", "flex")
        const keyName = row.append("div")
            .attr("class", "card-keyname")
            .html(k)
        const value = row.append("div")
            .attr("class", "card-value")
        if ((Array.isArray(d[k]) && d[k].length === 0) || d[k] === "") {
            value
                .html("None")
                .style("font-style", "italic")
        }
        else {
            value.html(d[k])

        }
    }


}

/**
 * Fetch the corresponding summary from the application.
 * @param {Object} d data
 * @param {int} index index of the category
 */
async function setSummary(d, index) {
    const collapsed = d3.select(`#accordion-collapsed-${index}`)
    fetch(`/summary/${d.path}`)
        .then(response => {
            if (!response.ok) throw new Error("Not found")
            return response.text()
        })
        .then(summary => {
            collapsed.html(summary)
        })
        .catch(err => {
            collapsed.html("<i>Error collecting summary, please restart the application.</i>")
        })
}

/**
 * Set or update the color of the card based on the page theme (dark/light) and 
 * the color of the focused node
 */
export function updateCardColors() {
    const focus = d3.select(".focus")
    if (!focus.empty()) {
        const focusCol = focus.datum().color
        const currentTheme = document.documentElement.getAttribute('data-bs-theme')
        const colorTheme = currentTheme === "light" ? "white" : "#212529"
        // checks the contrast between the focus color and the theme background color
        const focusColContrast = adjustColorContrast(colorTheme, focusCol)

        const colBgHeader = currentTheme === "light" ? focusCol : "#2B3035"
        const colTitleHeader = currentTheme === "light" ? "white" : focusColContrast

        // apply style
        d3.selectAll(".button-card").style("color", focusColContrast)
        d3.select("#cardheader")
            .style("background-color", colBgHeader)

        d3.select(".card-header-text").style("color", colTitleHeader)
        d3.select("#icon-card-header").style("color", colTitleHeader)

    }
}