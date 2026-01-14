import { zoom } from "./zoom.js"

/**
 * Sort files according to a key (rankKey)
 * @param {Object} tree tree's data
 * @param {string} rankKey Sorting key
 * @param {boolean} worstIsBiggest Worst performers are the biggest (True) or the smallest (False)
 */
export function createRanking(tree, rankKey, worstIsBiggest = true) {
    // takes only files
    const files = tree.descendants().filter(d => !d.children)
    let ranking

    if (worstIsBiggest) { // ascending order (= worst file is in first pos)
        ranking = files.sort((a, b) => b.data[rankKey] - a.data[rankKey])
    }
    else { // descending order (= worst file is in last pos)
        ranking = files.sort((a, b) => a.data[rankKey] - b.data[rankKey])
    }

    return ranking
}


/**
 * Set the worst performers list
 * @param {Object} tree tree's data
 * @param {string} cKey Color key
 * @param {boolean} worstIsBiggest Worst performers are the biggest (True) or the smallest (False)
 */
export function findWorst(tree, cKey) {
    const ranking = createRanking(tree, cKey)
    const isCont = d3.select("#legend").attr("type") === "cont"

    if (isCont) {
        d3.select("#worst-title").attr("hidden", null)
        d3.select("#worst").attr("hidden", null)
        for (let i = 0; i < 10; i++) {
            if (ranking[i]) {
                d3.select(`#worst-${i}`).html(ranking[i].data.name)
                .on("click", () => zoom(ranking[i]))
            }
        }
    }
    // hide it if cat color scale
    else {
        d3.select("#worst-title").attr("hidden", true)
        d3.select("#worst").attr("hidden", true)
    }
}