import { zoomTo, zoom } from "./zoom.js"
import { onMouseEnter, onMouseLeave } from "./mouseevent.js"
import { changeColor, setColor } from "./color.js"
import { searchElement } from "./search.js"
import { findWorst } from "./worst_performers.js"
import { initCard, updateCardColors } from "../general/MMAP/card.js"
import { createColorScale } from "../general/MMAP/color_scale.js"
import { colorPicker } from "../general/MMAP/color_palette_picker.js"
import { initGradient, initTheme, setGradient } from "../general/MMAP/page.js"
import { openCode } from "../general/MMAP/openCode.js"

let WIDTH = window.innerWidth
let HEIGHT = window.innerHeight
const searchInput = d3.select("#searchInput")

export async function circularPacking(
    title,
    path = "",
    colorRules = {},
    isSummary = false
) {
    let cKey
    const cselect = d3.select("#cselect")
    const log10 = d3.select("#log10")
    const legend = d3.select("#legend")
    let isLog = false
    let colorPalette = { "cat": "Observable10", "cont": "plasma" }

    /* -------------------------------------------------------------------------- */
    /*                                 FORMAT DATA                                */
    /* -------------------------------------------------------------------------- */

    const data = await d3.json("/data")
    data.sKey = "NLOC"
    let tree = formatData(data)

    tree.each(function (el, i) {
        el.index = i
        el.name = el.data.name
    })

    /* -------------------------------------------------------------------------- */
    /*                                  INIT PAGE                                 */
    /* -------------------------------------------------------------------------- */

    // init page theme (light/dark mode)
    const themeColor = initTheme()

    // color selector
    const excludeKey = ["children", "path", "name", "lines", "sKey"]
    for (let key in data) {
        if (!excludeKey.includes(key)) {
            cselect.append("option").html(key).attr("value", key)
        }
    }
    if (colorRules && Object.keys(colorRules).length > 0) { // custom color scheme
        cselect.append("option").html("custom").attr("value", "custom")
        tree.each(n => {
            const col = Object.keys(colorRules).find(key => n.data.path.includes(key)) ?? "undefined"
            n.data.custom = col
        })
    }

    // create color legend
    cKey = cselect.property("value")
    setColor(tree, cKey, isLog, colorRules, colorPalette)

    // repo name
    d3.select("#repo-name").html("The nesting of " + title)

    // worst performers
    const worst = d3.select("#worst")
    for (let i = 0; i < 10; i++) {
        worst.append("p")
            .attr("class", "worst-list")
            .attr("id", `worst-${i}`)
    }
    findWorst(tree, cKey)

    /* -------------------------------------------------------------------------- */
    /*                                  INIT SVG                                  */
    /* -------------------------------------------------------------------------- */

    const node = initSvg(tree, cKey)
    node
        //interaction
        .on("click", (event, d) => {
            if (event.metaKey || event.ctrlKey) {
                const filename = d.data.path.split(":")[0]
                openCode(path, filename, d.data.lines)
            }
            else {
                zoom(d)
            }
        })

    initCard(tree.data, ["children", "custom"], isSummary)

    /* -------------------------------------------------------------------------- */
    /*                                  LISTENERS                                 */
    /* -------------------------------------------------------------------------- */

    setCommonListeners(tree, data)
    // color related
    cselect.on("click", function () {
        const legend = d3.select("#legend")
        const popover = bootstrap.Popover.getInstance(legend)
        if (popover) {
            popover.dispose()
        }
    })
    cselect.on("change", function () {
        cKey = this.value
        changeColor(tree, cKey, isLog, colorRules, colorPalette)
        findWorst(tree, cKey)
        cselect.node().blur()
    })
    log10.on("change", function () {
        isLog = !isLog
        changeColor(tree, cKey, isLog, colorRules, colorPalette)
    })

    legend.on("click", function () {
        const legend = this
        const popover = colorPicker.call(legend, cKey, colorPalette)
        if (popover) {
            d3.select("#paletteSelect")
                .on("change", function () {
                    const type = legend.getAttribute("type")
                    colorPalette[type] = this.value
                    changeColor(tree, cKey, isLog, colorRules, colorPalette)
                    popover.dispose()
                }
                )
        }
    })

    // view settings
    setListenersView(tree, "NLOC")

}


export function nobvisual(data,
    title,
    legend = [],
) {
    const isCard = false

    // convert legend (array) to object
    const colorRules = Object.fromEntries(
        legend.map(([key, value]) => [key, value])
    )
    data.sKey = "datum"

    let tree = formatData(data)
    // set data
    tree.each(function (el, i) {
        el.index = i
        el.name = el.data.text
        el.color = el.data.color
        const col = Object.entries(colorRules).find(([_, value]) => value === el.color)
        el.data.custom = col ? col[0] : "undefined"
    })



    /* -------------------------------------------------------------------------- */
    /*                                  INIT PAGE                                 */
    /* -------------------------------------------------------------------------- */

    // init page theme
    initTheme()

    // color scale
    const color = createColorScale([], "custom", false, colorRules)

    d3.select("#title").html(title)

    /* -------------------------------------------------------------------------- */
    /*                                  INIT SVG                                  */
    /* -------------------------------------------------------------------------- */

    const node = initSvg(tree, "custom")
    node
        //interaction
        .on("click", (event, d) => {
            zoom(d, isCard)
        })

    /* -------------------------------------------------------------------------- */
    /*                                  LISTENERS                                 */
    /* -------------------------------------------------------------------------- */

    setCommonListeners(tree, isCard)
    setListenersView(tree, "datum")
}


/**
 * Hierarchize input data and set a packed layout (circular packing).
 * @param {Object} data JSON data
 * @param {string} sKey Size key
 * @param {number} padding Padding value
 * @param {Array} size View size (screen size by default)
 * @returns hierarchical data (tree's data) with the following properties:
 *  - node.x : the x-coordinate of the circle’s center
 *  - node.y : the y coordinate of the circle’s center
 *  - node.r : the radius of the circle
 */
function formatData(data, sameSize = false, padding = Math.round(WIDTH / 2 * 0.005)) {
    const sKey = data.sKey

    // packing
    let pack = d3.pack()
        .size([WIDTH, HEIGHT])
        .padding(padding)

    // hierarchy
    let root
    if (!sameSize) {
        root = d3.hierarchy(data)
            .sum(d => d[sKey])
    }
    else {
        root = d3.hierarchy(data)
            .sum(d => d[sKey] > 0 ? 1 : 0) // avoid "empty" circles
    }

    const tree = pack(root)

    return tree
}


/**
 * Init main svg :  
 *     - create circles  
 *     - init tooltip  
 *     - set view   
 *     - set opacity gradient underneath the menu
 * 
 * @param {Object} tree tree's data
 * @param {String} cKey color key
 * @returns selection of circles
 */
function initSvg(tree, cKey) {
    // set svg
    const svg = d3.select("#svg")
        .attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`)
        .attr("style", "width: 100%; height: auto; font: 10px sans-serif; display:block;")
    const view = svg
        .append("g")
        .attr("transform", `translate(${WIDTH / 2}, ${HEIGHT / 2})`)
        .attr("id", "view")
    const foreground = svg.append("g")
        .attr("transform", `translate(${WIDTH / 2}, ${HEIGHT / 2})`)
        .attr("id", "foreground")


    // create circles
    const node = view
        .selectAll(".circle")
        .data(tree)
        .join("circle")
        .attr("id", (_, i) => `circle-${i}`)
        // custom class
        .classed("circle", true)
        .classed("focus", false)
        .attr("fill", d => d.children ? d3.interpolateRgb(d.color, "white")(0.7) : d.color)
        .attr("stroke", d => d.children ? d.color : "null")
        .attr("stroke-width", 1)
        // tooltip
        .attr("data-bs-title", d => `<b>${d.name}</b><br>${d.data[cKey]}`)
        .attr("data-bs-toggle", "tooltip")
        .attr("data-bs-trigger", "manual")
        .attr("data-bs-custom-class", "custom-tooltip")
        .attr("data-bs-html", "true")
        .on("mouseover", onMouseEnter)
        .on("mouseout", onMouseLeave)

    // init circular text
    node.each(function (d) {
        foreground.append("path")
            .datum({ x: d.x, y: d.y, r: d.r, index: d.index })
            .attr("class", "circlePath")
            .attr("id", `circlePath-${d.index}`)

        foreground.append("text").append("textPath")
            .datum({ x: d.x, y: d.y, r: d.r, index: d.index })
            .attr("startOffset", "50%")
            .attr("id", `circleText-${d.index}`)
            .attr("href", `#circlePath-${d.index}`)
            .text(d.name)
            .style("fill", d.color)
    })
    const rootColor = d3.color(tree.color).copy({ opacity: 0.2 })
    document.documentElement.style.setProperty('--root-color', rootColor)


    // initial view
    d3.select("#circle-0").classed("focus", true)
    const include = tree.descendants().map(d => d.index)
    zoomTo([tree.x, tree.y, tree.r * 2.5], include)
    // updateCircularText()

    initGradient()

    return node
}


/**
 * Set common listeners (search, click on background, help card) 
 * between nobvisual and mmap
 * @param {Object} tree tree's data
 * @param {Boolean} isCard show card (true) or not (false).
 */
function setCommonListeners(tree, isCard = true) {
    const svg = d3.select("#svg")

    // reboot 
    document.addEventListener("click", function (event) {
        const table = d3.select(".table-responsive")
        // click on the background -> reset zoom
        if (event.target == svg.node()) {
            zoom(tree, isCard)
        }
        // click anywhere on the svg (background+elements)
        // -> reboot seach
        d3.select("#searchInput").property("value", "")
            .attr("class", "form-control")
        d3.select("#tablebody").selectAll("tr").remove()
        table.attr("hidden", true)
        d3.select("#errorinfo").remove()

        const legend = d3.select("#legend").node()
        const popoverEl = document.querySelector('.popover')
        if (!legend.contains(event.target) && !(popoverEl && popoverEl.contains(event.target))) {
            const popover = bootstrap.Popover.getInstance(legend)
            if (popover) {
                popover.dispose()
            }
        }

    })

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
        if (previousTheme === "light") {
            borders.forEach(el => el.classList.replace("border-dark", "border-white"))
            menuEl.style("color", "white")
        }
        else {
            borders.forEach(el => el.classList.replace("border-white", "border-dark"))
            menuEl.style("color", "black")
        }
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
            searchElement(event, tree, isCard)
        }

    })

    // help card
    d3.select("#help").on("click", function () {
        const modalElement = document.getElementById('helpModal')
        const modalInstance = new bootstrap.Modal(modalElement)
        modalInstance.show()
    })

    // setting card
    d3.select("#settings").on("click", function () {
        const modalElement = document.getElementById('settingModal')
        const modalInstance = new bootstrap.Modal(modalElement)
        modalInstance.show()
    })

}

/**
 * Set listeners for view settings modal.
 *      - zoom input
 *      - padding input
 *      - same size check
 * 
 * Common between nobs and tree
 * 
 * Open/close is handled by Bootstrap (see HTML page).
 * 
 * @param {Object} tree tree's data
 * @param {string} sKey Size key
 */
function setListenersView(tree, sKey) {

    // init 
    const initPadding = Math.round(WIDTH / 2 * 0.005)
    const paddingInput = d3.select("#padding-input")
    paddingInput.property("max", initPadding * 3.5)
    // (max - initPadding) + min = (initPadding * 3.5 - initPadding) + 0
    paddingInput.property("value", initPadding * 2.5)


    d3.select("#zoom-input").on("change", function () {

        let zoom = this.max - (this.value - this.min)
        const include = tree.descendants().map(d => d.index)
        const focus = d3.select(".focus").datum()
        const zoomFactor = (focus.data.children.length == 0) ? zoom * 2 : zoom
        zoomTo([focus.x, focus.y, focus.r * zoomFactor], include)
        d3.select(".pulse").attr("r", window.innerHeight / zoomFactor)
    }
    )
    d3.select("#padding-input").on("change", function () {
        rebootView(tree, sKey)
    })

    d3.select("#sameSize").on("change", function () {
        rebootView(tree, sKey)
    })

    // reset default
    //   - zoom = 2.5 
    //   - padding = initPadding
    //   - same size = false
    // (closing handled by Bootstrap)
    d3.select("#resetDefault").on("click", function () {
        const zI = d3.select("#zoom-input")
        const zIvalue = (zI.property("max") - 2.5) + parseInt(zI.property("min"))
        zI.property("value", zIvalue)
        // (max - initPadding) + min = (initPadding * 3.5 - initPadding) + 0
        d3.select("#padding-input").property("value", initPadding * 2.5)
        d3.select("#sameSize").property("checked", false)

        rebootView(tree, sKey)
    })

    window.addEventListener("resize", () => {
        rebootView(tree, sKey)
    })

}

/**
 * Reboot the view after editing view settings: 
 *      - padding level
 *      - zoom level
 *      - size (= or not)
 * 
 * **WARNING** : this function changes the variable tree (main data).
 * 
 * @param {Object} tree Tree's data
 * @param {string} sKey Size key
 * @returns Modified tree's data
 */
function rebootView(tree, sKey) {
    const pI = d3.select("#padding-input")
    const sameSize = d3.select("#sameSize").property("checked")
    const zI = d3.select("#zoom-input")

    // sliders are reversed:
    //   
    // zoom out     default    zoom in
    //              <--|-->   
    //     |-----------o-----------|
    //  max val (=3.5)          min val (=2)
    //
    // property("min") = max value 
    // property("max") = min value
    // min >> max ==> UNCORRECT ! 
    //
    // => scaling = max - (value - min)

    const zoom = zI.property("max") - (zI.property("value") - zI.property("min"))
    const padding = pI.property("max") - (pI.property("value") - pI.property("min"))
    let newtree

    newtree = formatData(tree.data, sameSize, padding)


    // edit x,y,r
    const nt = newtree.descendants()
    tree.each(function (el, i) {
        el.x = nt[i].x
        el.y = nt[i].y
        el.r = nt[i].r
    })

    d3.selectAll(".circle").each(function (d) {
        d3.select(`#circlePath-${d.index}`)
            .datum({ x: d.x, y: d.y, r: d.r, index: d.index })
        d3.select(`#circleText-${d.index}`)
            .datum({ x: d.x, y: d.y, r: d.r, index: d.index })
    })

    const include = tree.descendants().map(d => d.index)
    const focus = d3.select(".focus").datum()
    const zoomFactor = (focus.data.children.length == 0) ? zoom * 2 : zoom
    zoomTo([focus.x, focus.y, focus.r * zoomFactor], include)
    d3.select(".pulse").attr("r", window.innerHeight / zoomFactor)
}