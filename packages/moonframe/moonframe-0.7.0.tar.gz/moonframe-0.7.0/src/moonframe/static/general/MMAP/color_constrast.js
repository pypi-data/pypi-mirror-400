function getLuminance(hex) {
    const rgb = hex.match(/\w\w/g).map(x => parseInt(x, 16) / 255);
    const a = rgb.map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
}

function contrast(c1, c2) {
    const L1 = getLuminance(c1);
    const L2 = getLuminance(c2);
    return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
}

/**
 * Compute contrast ratio between background and text color (black and white only)
 * if it’s below the threshold (4.5:1 for normal text), switch to the opposite text color (black : white).
 * @param {String} bg background color
 * @param {String} txt text color (black and white only)
 * @returns new text color that constrast with the background 
 */
export function adjustColorConstrast_BW(bg, txt) {
    const hbg = d3.color(bg).hex()
    const htxt = d3.color(txt).hex()
    const inverse = { "white": "black", "black": "white" }
    return contrast(hbg, htxt) < 4.5 ? inverse[txt] : txt
}


/**
 * Ensures that a given text color has sufficient contrast against 
 * a background color by adjusting it toward either black or white
 * @param {String} bg background color
 * @param {String} txt text color
 * @returns new text color that contrast with the background
 */
export function adjustColorContrast(bg, txt) {
    const threshold = 4.5
    const hbg = d3.color(bg).hex();
    const htxt = d3.color(txt).hex();
    const whiteBG = getLuminance(hbg) > 0.5

    // good constrast -> return the initial color
    if (contrast(hbg, htxt) > threshold) {
        return txt
    }

    const target = whiteBG ? "black" : "white";
    const interp = d3.interpolateRgb(htxt, target)

    let t = target
    // finds the minimum interpolation factor that makes text readable
    for (let step = 0; step <= 1; step += 0.1) {
        const candidate = d3.color(interp(step)).hex()
        if (contrast(hbg, candidate) > threshold) {
            t = candidate
            break
        }
    }

    return t
}