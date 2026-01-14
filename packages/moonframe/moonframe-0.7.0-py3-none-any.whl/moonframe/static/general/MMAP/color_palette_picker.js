import { catPalettes, palettes } from "../palettes.js"

/**
 * colorPicker displays or hides (depending on the case) a small popover so that
 * the user can choose a new color palette
 * @param {String} cKey color key
 * @param {Object} colorPalette color palette choice : {"cont" : ..., "cat" : ...}
 * @returns bootstrap Popover object
 */
export function colorPicker(cKey, colorPalette = {"cont" : "plasma", "cat" : "Observable10"}) {
    let popover = bootstrap.Popover.getInstance(this)

    if (popover) {
        popover.dispose()
        return 
    }

    else {
        if (cKey !== "custom") {

            popover = new bootstrap.Popover(this, {
                content: document.getElementById('palette-popover').innerHTML,
                html: true,
                container: 'body',
                sanitize: false,
                offset: [0, 50],

            })
            popover.show()

            const type = d3.select("#legend").attr("type")
            const paletteSelect = d3.select("#paletteSelect")
            const paletteType = type === "cont" ? palettes : catPalettes
            const palette = Object.keys(paletteType)

            for (let pal of palette) {
                paletteSelect.append("option").html(pal).attr("value", pal)
            }
            paletteSelect.property("value", colorPalette[type])
        }
        return popover


    }
}