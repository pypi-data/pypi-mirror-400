
/**
 * Init opacity gradient underneath the menu
 */
export function initGradient() {
    const HEIGHT = window.innerHeight
    const svg = d3.select("#svg")
    
    const gradient = svg.append("defs")
        .append("linearGradient")
        .attr("id", "fade-gradient")
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "100%").attr("y2", "0%")

    setGradient()

    svg.append("rect")
        .attr("id", "mask")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", "500px")
        .attr("height", HEIGHT)
        .attr("fill", "url(#fade-gradient)")
        .style("pointer-events", "none")
}

/**
 * Set gradient underneath the menu depending on the page theme (light/dark)
 */
export function setGradient() {
    const gradient = d3.select("#fade-gradient")
    const currentTheme = document.documentElement.getAttribute('data-bs-theme')
    const darkCol = getComputedStyle(document.documentElement)
        .getPropertyValue('--bs-body-bg')
        .trim()
    const color = currentTheme === "dark" ? darkCol : "white"

    gradient.selectAll("stop").remove()

    gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", color)
        .attr("stop-opacity", 0.8)

    gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", color)
        .attr("stop-opacity", 0)
}

/**
 * Init page theme between light/dark based on user settings
 * @returns theme ("light" or "dark")
 */
export function initTheme() {
    // get the user preferences for the theme (light/dark)
    const themetoggle = d3.select("#themeToggle")
    const border = d3.selectAll(".border")
    const colorMode = window.matchMedia("(prefers-color-scheme: dark)").matches ?
        "dark" :
        "light"
    document.documentElement.setAttribute("data-bs-theme", colorMode)
    themetoggle.classed("active", colorMode === "light" ? true : false)
    const menuEl = d3.select("#bottom-right-menu")
    if (colorMode === "light") {
        border.classed("border-dark", true)
        menuEl.style("color", "black")
    }
    else {
        border.classed("border-white", true)
        menuEl.style("color", "white")
    }

    return colorMode
}
