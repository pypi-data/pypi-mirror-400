import { AppState } from "./global.js"
import { changeColor, setColor } from "./color.js"
import { selectPoint, unfocus } from "./clickevent.js"
import { onMouseEnter, onMouseLeave, highlightPath, showTooltip, hideTooltip, clearPathHighlight, updateTooltip } from "./mouseevent.js"
import { searchElement } from "./search.js"
import { createSizeScale, changeSize } from "./size.js"
import { setHulls, updateHulls, showHulls, resetHulls } from "./hulls.js"
import { initGradient, initTheme, setGradient } from "../general/MMAP/page.js"
import { initCard, updateCardColors } from "../general/MMAP/card.js"
import { colorPicker } from "../general/MMAP/color_palette_picker.js"
import { adjustColorContrast } from "../general/MMAP/color_constrast.js"
import { openCode } from "../general/MMAP/openCode.js"

export async function callgraph(data_path, repo_path, repo_name, color_rules) {
    const WIDTH = window.innerWidth
    const HEIGHT = window.innerHeight
    const symbol = d3.symbol()
    let isDragging = false
    let isZoomWithSlider = false
    let colorPalette = { "cat": "Observable10", "cont": "plasma" }
    let isLog = false

    /* -------------------------------------------------------------------------- */
    /*                                  SELECTOR                                  */
    /* -------------------------------------------------------------------------- */

    const cselect = d3.select("#cselect")
    const sselect = d3.select("#sselect")
    const log10 = d3.select("#log10_checkbox")
    const seeFiles = d3.select("#seefilescheck")
    const zoomSlider = d3.select("#zoom-slider")
    const zoomButton = d3.select(".bi-zoom-in")
    const resetZoom = d3.select("#reset-zoom")
    const searchInput = d3.select("#searchInput")
    const legend = d3.select("#legend")

    /* -------------------------------------------------------------------------- */
    /*                              DATA MANIPULATION                             */
    /* -------------------------------------------------------------------------- */

    const data = await d3.json(data_path)
    const links = data.links.map(d => ({ ...d }))
    // to catch the root and the leaves
    const sources = new Set(links.map(link => link.source))
    const targets = new Set(links.map(link => link.target))
    const nodes = data.nodes.map(d => ({ ...d }))
        // remove solitary
        .filter(d => (targets.has(d.id) || sources.has(d.id)))

    nodes.forEach(function (el, i) {
        el.index = i
    })

    /* -------------------------------------------------------------------------- */
    /*                                  INIT PAGE                                 */
    /* -------------------------------------------------------------------------- */

    const themeColor = initTheme()

    // init select for scales
    for (let key of Object.entries(nodes[0])) {
        // ignore "useless" categorical metrics : 
        // = those that have only one category or as many categories as points
        const domain = [... (new Set(nodes.map(d => d[key[0]])))]
        const isNotNum = typeof domain[0] !== "number"
        // list of keys to be removed that pass length filters
        const exclude = ["linestart", "name", "filename", "index", ""]
        if (!(isNotNum && (domain.length === 1 || domain.length === nodes.length)
            || exclude.includes(key[0]))) {
            cselect.append("option").html(key[0]).attr("value", key[0])
            if (!isNotNum) { // create size select
                sselect.append("option").html(key[0]).attr("value", key[0])
            }
        }
    }
    if (color_rules && Object.keys(color_rules).length > 0) { // custom color scheme
        cselect.append("option").html("custom").attr("value", "custom")
        nodes.forEach(n => {
            const col = Object.keys(color_rules).find(key => n.id.includes(key)) ?? "undefined"
            n.custom = col
        })
    }


    let cKey = cselect.property("value")
    let sKey = sselect.property("value")
    // create color legend
    setColor(nodes, cKey, isLog, colorPalette)
    createSizeScale(nodes, sKey)

    // repo name
    d3.select("#repo-name").html("The structure of " + repo_name)

    // help card
    d3.select("#help").on("click", function () {
        const modalElement = document.getElementById('helpModal')
        const modalInstance = new bootstrap.Modal(modalElement)
        modalInstance.show()
    })

    /* -------------------------------------------------------------------------- */
    /*                                  INIT SVG                                  */
    /* -------------------------------------------------------------------------- */

    // force X and for force Y (for clustering)
    let inposX = []
    let counterX = 1
    let inposY = []
    const nbNodes = nodes.length
    function getOrAssignX(d) {
        if (!inposX[d.filename]) {
            inposX[d.filename] = (WIDTH / nbNodes) * counterX
            counterX++
        }
        return inposX[d.filename]
    }
    function getOrAssignY(d) {
        if (!inposY[d.filename]) {
            inposY[d.filename] = HEIGHT / (Math.random() * (d.filename.length + 1) + 1)
        }
        return inposY[d.filename]
    }
    // create forces
    const simulation = d3.forceSimulation(nodes)
        .on("tick", ticked)
        .force('x', d3.forceX(getOrAssignX))
        .force('y', d3.forceY(getOrAssignY))
        .force("link", d3.forceLink(links).id(d => d.id)
            .strength(function (l) {
                if (l.source.filename === l.target.filename) {
                    // stronger link for links within a group
                    return 2
                }
                else {
                    return 0.01
                }
            }))
        .force("charge", d3.forceManyBody().strength(-600))
        .force("center", d3.forceCenter(WIDTH / 2, HEIGHT / 2))
        .force("collide", d3.forceCollide(17))
    //performances
    simulation.alphaMin(0.005)

    // set svg
    const svg = d3.select("#svg")
        .attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`)
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;")

    // performance hack : use opacity mask
    // so order is important :
    // svg
    // └── (g) foreground
    //     ├── (circle) flags
    //     └── (g) orbit container 
    //         └── (g) orbit group 
    // ├── (g) view
    // |   ├── (rect) main opacity mask (hidden)
    // |   ├── (path) nodes 
    // |   ├── (line) links
    // |   └── (path) convex hulls

    const view = svg.append("g").attr("id", "view")
    setHulls(nodes)
    // foreground
    const foreground = svg.append("g").attr("id", "foreground")

    initGradient()

    const mask = view.append("rect")
        .attr("class", "fade-mask")
        .style("opacity", themeColor === "light" ? "0.9" : "0.8")
        .style("pointer-events", "none")
        .style("fill", themeColor === "light" ? "white" : "black")
        .style("visibility", "hidden")

    // set zoom
    const zoom = d3.zoom()
        .on("zoom", (event) => {
            const t = event.transform
            view.attr("transform", t)
            foreground.attr("transform", t)

            if (!isZoomWithSlider) {
                zoomSlider.property("value", t.k)
            }

            // calc opacity mask layer
            const topLeft = t.invert([0, 0])
            const bottomRight = t.invert([window.innerWidth, window.innerHeight])

            const x = topLeft[0]
            const y = topLeft[1]
            const width = bottomRight[0] - x
            const height = bottomRight[1] - y

            mask
                .attr("x", x)
                .attr("y", y)
                .attr("width", width)
                .attr("height", height)


            d3.selectAll(".flag, .focus, .hover, .focusHull").each(function () {
                updateTooltip(this)
            })
        })
    svg.call(zoom)
    // set first view
    svg.call(zoom.transform, d3.zoomIdentity.scale(0.2).translate(WIDTH / 0.5, HEIGHT / 0.5))

    // set links
    const link = view
        .selectAll()
        .data(links)
        .join("line")
        .classed("linkline", true)
        .classed("linkInHull", false)
        .classed("hide", false)
        .attr("stroke", d => d.source.color)
        .attr("data-id", d => `link-${d.source.id}`)
        .attr("marker-end", (d, i) => setArrow(d.source.color, d.target.size, i))

    // set nodes
    const node = view
        .selectAll()
        .data(nodes)
        .join("path")
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        // different symbols
        .attr("d", d => {
            if (!targets.has(d.id)) return symbol.type(d3.symbolStar).size(d.size)()
            if (!sources.has(d.id)) return symbol.type(d3.symbolSquare).size(d.size)()
            return symbol.type(d3.symbolCircle).size(d.size)() // default
        })
        .attr("fill", d => d.color)
        .style("--fill-color", d => d.color)
        // .style("filter", d => `drop-shadow(0px 0px 10px ${d.color}`)
        .attr("data-id", d => `node-${d.id}`)
        // tooltip
        .attr("data-bs-toggle", "tooltip")
        .attr("data-bs-title", d => d.name)
        .attr("data-bs-trigger", "manual")
        // custom classes
        .classed("nodes", true)
        .classed("flag", false)
        .classed("hide", false)
        .classed("selectInPath", false)
        .classed("selectInHull", false)
        .classed("focus", false)
        .classed("hover", false)
        // events
        .on("click", function (event, d) {
            if (event.metaKey || event.ctrlKey) {
                openCode(repo_path, d.filename, d.lines)
            }
            else {
                selectPoint(this, d)
            }
        })
        .on("mouseenter", onMouseEnter)
        .on("mouseleave", onMouseLeave)

    mask.raise()

    // set moving dots (at selection)
    const orbit = foreground.append("g")
        .attr("class", "orbit-container")
    const orbitgroup = orbit.append("g").attr("class", "orbit-group")

    const exclude = ["index", "x", "y", "vx", "vy", "fx", "fy", "aggregated", "callables", "annotations", "custom", "color", "weight", "statements", "parents", "contains", "id", "lang", "path"]
    initCard(nodes[0], exclude)

    /* -------------------------------------------------------------------------- */
    /*                                  LISTENERS                                 */
    /* -------------------------------------------------------------------------- */

    // reboot 
    document.addEventListener("click", function (event) {
        const table = d3.select(".table-responsive")
        const focus = d3.select(".focus")

        // click on the background :
        if ((event.target === svg.node() || link.nodes().includes(event.target)) && !focus.empty()) {
            unfocus()
        }
        // click anywhere on the svg (background+elements)
        // reboot seach
        d3.select("#searchInput").property("value", "")
            .attr("class", "form-control")
        d3.select("#tablebody").selectAll("tr").remove()
        table.attr("hidden", true)
        d3.select("#errorinfo").remove()

        // color palette picker
        const legendEl = legend.node()
        const popoverEl = document.querySelector('.popover')
        if (!legendEl.contains(event.target) && !(popoverEl && popoverEl.contains(event.target))) {
            const popover = bootstrap.Popover.getInstance(legendEl)
            if (popover) {
                popover.dispose()
            }
        }
    })

    // drag
    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // color related
    cselect.on("click", function () {
        const legend = d3.select("#legend")
        const popover = bootstrap.Popover.getInstance(legend)
        if (popover) {
            popover.dispose()
        }
    })
    cselect.on("change", function (event) {
        cKey = this.value
        changeColor(nodes, cKey, isLog, color_rules, colorPalette)
        cselect.node().blur()
    })
    log10.on("change", function () {
        isLog = !isLog
        changeColor(nodes, cKey, isLog, color_rules, colorPalette)
    })

    // see files
    seeFiles.on("change", function () {
        AppState.isHullVisible = !AppState.isHullVisible
        // hide convex hulls
        if (!AppState.isHullVisible) {
            // set color to default
            cselect.select("#filenames").remove()
            cKey = cselect.property("value")
            changeColor(nodes, cKey, isLog, color_rules, colorPalette)
            cselect.attr("disabled", null)
            log10.attr("disabled", null)
            // hide hulls + mask hull
            resetHulls()
            d3.selectAll(".hull").style("visibility", "hidden")
            legend.style("display", "block")
        }
        // show convex hulls
        else {
            // set color to filename
            cselect.append("option").html("filenames").attr("value", "filenames").attr("id", "filenames")
            cselect.property("value", "filenames")
            legend.style("display", "none")
            cKey = "filename"
            // then disable color change
            cselect.attr("disabled", true)
            log10.attr("disabled", true)
            // show hulls
            showHulls(colorPalette)
        }
    })

    // size
    sselect.on("change", function () {
        sKey = this.value
        changeSize(nodes, targets, sources, sKey)
    })

    // search
    searchInput.on("click", function () {
        // reboot
        searchInput.attr("class", "form-control")
        d3.select("#errorinfo").remove()
    })

    // keyboard (on search bar)
    searchInput.on('keyup', function (event) {
        // reboot
        searchInput.attr("class", "form-control")
        d3.select("#tablebody").selectAll("tr").remove()
        d3.select("#errorinfo").remove()

        // user deletes their input
        if (event.key == "Backspace" && searchInput.property("value") === "") {
            d3.select(".table-responsive").attr("hidden", true)
        }
        // else : search
        else {
            searchElement(event, nodes)
        }
    })

    // keyboard (general)
    document.addEventListener("keydown", function (event) {
        const focus = d3.select(".focus")
        const hover = d3.select(".hover")
        // hide point on "h"
        if (event.key === "h") {
            if (!hover.empty()) {
                const data = hover.datum()

                // hide point
                hover.classed("hide", true)
                // hide parent links
                const sources = link.filter(l => l.target.id === data.id)
                    .each(function (l) {
                        d3.select(this).classed("hide", true)
                    })
                // hide children links
                const target = link.filter(l => l.source.id === data.id)
                    .each(function (l) {
                        d3.select(this).classed("hide", true)
                    })

                // special handle for the flags
                if (hover.classed("flag") === true) {
                    hover.classed("flag", false)
                    svg.select(`#circle-flag-${data.index}`).remove()
                }
                // hulls
                if (AppState.isHullVisible) {
                    updateHulls()
                }
                // special handle when there is a focusPoint
                if (!focus.empty()) {
                    // if the point is a focusPoint : unfocus it
                    if (hover.node() === focus.node()) {
                        unfocus()
                    }
                    else {
                        // if the point was in the selected point path : recreate path
                        // = ignore the children of the hidden point
                        if (hover.classed("selectInPath") === true) {
                            clearPathHighlight()
                            highlightPath(focus.datum().id)
                        }
                        // else... nothing change
                        // but in practice, "else" case never happens because 
                        // the hover event is limited to points in the path
                    }
                }
                else {
                    clearPathHighlight()
                }
                // simulation
                resetSimulation()

                // tooltip
                hideTooltip(hover.node())
                hover.classed("hover", false)

            }
        }
        // flag point on "f"
        else if (event.key == "f") {
            const hover = d3.select(".hover")
            if (!hover.empty()) {
                hover.style("stroke", null)
                const data = hover.datum()
                const index = data.index
                // set flag
                if (hover.classed("flag") === false) {
                    const bg = themeColor === "light" ? "white" : "black"
                    const colorFlag = adjustColorContrast(bg, data.color)
                    hover.classed("flag", true)
                    showTooltip(hover.node(), data.color)
                    foreground.append("circle")
                        .attr("id", `circle-flag-${index}`)
                        .attr("class", "circle-flag")
                        .attr("r", Math.sqrt(data.size + 2))
                        .style("fill", colorFlag)
                        .style("stroke", colorFlag)
                        .attr("cx", data.x)
                        .attr("cy", data.y)
                        .attr("opacity", "0.5")
                        .style("pointer-events", "none")
                        .lower()
                }
                // delete flag
                else {
                    hover.classed("flag", false)
                    svg.select(`#circle-flag-${index}`).remove()
                }
            }
        }
        // remove all flags
        else if (event.key == "F" && event.shiftKey) {
            const flag = d3.selectAll(".flag")
                .classed("flag", false)

            flag.each(function () {
                const tooltip = bootstrap.Tooltip.getInstance(this)
                tooltip.dispose()
            })
            svg.selectAll(".circle-flag").remove()
        }
        // show all points on "shift+h" or... "H" 
        else if (event.key == "H" && event.shiftKey) {
            d3.selectAll(".hide").classed("hide", false)
            resetSimulation()
            if (!focus.empty()) {
                const id_focus = focus.attr("data-id").split("-")[1]
                highlightPath(id_focus)
            }
            if (AppState.isHullVisible) {
                updateHulls()
            }
        }
    })

    zoomButton.on("click", () => zoomSlider.style("visibility") === "visible" ? zoomSlider.style("visibility", "hidden") : zoomSlider.style("visibility", "visible"))
    zoomSlider.on("change", function () {
        const sliderlvl = this.value
        const currentlvl = d3.zoomTransform(view.node()).k
        const zoomlvl = sliderlvl / currentlvl
        isZoomWithSlider = true
        svg.transition().duration(300)
            .call(zoom.scaleBy, zoomlvl)
            .on("end", () => { isZoomWithSlider = false })
    })

    resetZoom.on("click", () => svg.call(zoom.transform, d3.zoomIdentity.scale(0.2).translate(WIDTH / 0.5, HEIGHT / 0.5)))


    // light/dark mode
    const themeToggle = document.getElementById('themeToggle')
    const htmlEl = document.documentElement

    themeToggle.addEventListener('click', () => {
        themeToggle.classList.toggle('active')
        const previousTheme = htmlEl.getAttribute('data-bs-theme')
        htmlEl.setAttribute('data-bs-theme', previousTheme === 'light' ? 'dark' : 'light')
        setGradient()
        updateCardColors()
        const menuEl = d3.select("#bottom-right-menu")
        const borders = document.querySelectorAll(".border")
        const fadeMask = d3.select(".fade-mask")
        if (previousTheme === "light") {
            borders.forEach(el => el.classList.replace("border-dark", "border-white"))
            menuEl.style("color", "white")
            fadeMask.style("fill", "black").style("opacity", "0.8")
        }
        else {
            borders.forEach(el => el.classList.replace("border-white", "border-dark"))
            menuEl.style("color", "black")
            fadeMask.style("fill", "white").style("opacity", "0.9")
        }
    })

    legend.on("click", function () {
        const legend = this
        const popover = colorPicker.call(legend, cKey, colorPalette)
        if (popover) {
            d3.select("#paletteSelect")
                .on("change", function () {
                    const type = legend.getAttribute("type")
                    colorPalette[type] = this.value
                    changeColor(nodes, cKey, isLog, color_rules, colorPalette)
                    popover.dispose()
                }
                )
        }
    })

    /* -------------------------------------------------------------------------- */
    /*                                 SIMULATION                                 */
    /* -------------------------------------------------------------------------- */


    /**
     *  Is called each time the simulation ticks : update position of all elements 
     */
    function ticked() {
        const visibleNodes = d3.selectAll(".nodes:not(.hide)")
        const focus = d3.select(".focus")

        // centroids 
        let alpha = this.alpha()
        let centroids = {}
        let coords = {}
        let groups = []

        // sort the nodes into groups:  
        visibleNodes.each(function (d) {
            if (groups.indexOf(d.filename) == -1) {
                groups.push(d.filename)
                coords[d.filename] = { x: d.x, y: d.y, n: 1 }
            }
            else {
                coords[d.filename].x += d.x
                coords[d.filename].y += d.y
                coords[d.filename].n += 1
            }
        })

        for (let group in coords) {
            let groupNodes = coords[group]
            let cx = groupNodes.x / groupNodes.n
            let cy = groupNodes.y / groupNodes.n

            centroids[group] = { x: cx, y: cy }
        }

        // adjust each point if needed towards group centroid:
        visibleNodes.each(function (d) {
            let cx = centroids[d.filename].x
            let cy = centroids[d.filename].y

            d.vx -= (d.x - cx) * 0.1 * alpha
            d.vy -= (d.y - cy) * 0.1 * alpha
        })

        visibleNodes
            .attr("transform", d => `translate(${d.x},${d.y})`)

        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            // shorten links so that they end at the node boundary
            .attr("x2", d => {
                const dx = d.target.x - d.source.x
                const dy = d.target.y - d.source.y
                const len = Math.sqrt(dx * dx + dy * dy)
                const r = Math.sqrt(d.target.size / Math.PI)
                return len === 0 ? d.target.x : d.target.x - (dx / len) * r
            })
            .attr("y2", d => {
                const dx = d.target.x - d.source.x
                const dy = d.target.y - d.source.y
                const len = Math.sqrt(dx * dx + dy * dy)
                const r = Math.sqrt(d.target.size / Math.PI)
                return len === 0 ? d.target.y : d.target.y - (dy / len) * r
            })

        // orbit
        if (!focus.empty()) {
            const d = focus.datum()
            orbit.attr("transform", `translate(${d.x},${d.y})`)
        }

        // tooltip(s)
        d3.selectAll(".flag, .focus, .hover, .focusHull").each(function () {
            updateTooltip(this)
        })

        // circle-flag
        svg.selectAll(".flag").each(function () {
            const data = d3.select(this).datum()
            const circle = d3.select(`#circle-flag-${data.index}`)
                .attr("cx", data.x)
                .attr("cy", data.y)
        }

        )

        // convex hulls
        if (AppState.isHullVisible) {
            updateHulls()
        }
    }


    /**
     * Is called when drag starts
     * @param {event} event 
     * @param {Object} d 
     */
    function dragstarted(event, d) {
        AppState.isItADrag = true
        isDragging = true
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    /**
     * Update the subject (dragged node) position during drag.
     * @param {event} event 
     */
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    /**
     * Is called at the end of drag
     * @param {*} event 
     * @param {*} d 
     */
    function dragended(event, d) {
        AppState.isItADrag = false
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    return svg.node();

    function resetSimulation() {
        const newNodes = node.filter(function () { return !d3.select(this).classed("hide") }).data()
        const newLinks = link.filter(function () { return !d3.select(this).classed("hide") }).data()
        simulation.nodes(newNodes)
            .force("link", d3.forceLink(newLinks).id(d => d.id)
                .strength(function (l) {
                    if (l.source.filename === l.target.filename) {
                        // stronger link for links within a groupH
                        return 2
                    }
                    else {
                        return 0.01
                    }
                }))
        simulation.alpha(0.1).restart()
    }
}

/* -------------------------------------------------------------------------- */
/*                              EXPORT FUNCTIONS                              */
/* -------------------------------------------------------------------------- */

/**
* Set the arrows at the end of the lines
* @param {Object} color color scale
* @returns 
*/
export function setArrow(color, size, icol) {
    const svg = d3.select("#svg")

    // reset if needed
    const lastArrow = svg.select(`#arrowhead-${icol}`)
    if (!lastArrow.empty()) {
        lastArrow.node().parentNode.remove()
    }

    const realSize = Math.sqrt(size / Math.PI) + 2
    const arrowSize = Math.trunc(realSize / 3)
    svg.append("defs").append("marker")
        .attr("id", `arrowhead-${icol}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", arrowSize)
        .attr("refY", 0)
        .attr("markerWidth", arrowSize)
        .attr("markerHeight", arrowSize)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", color)

    return `url(#arrowhead-${icol})`;
}