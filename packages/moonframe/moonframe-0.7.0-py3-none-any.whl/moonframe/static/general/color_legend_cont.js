/**
 * Copyright 2021, Observable Inc.
 * Released under the ISC license.
 * https://observablehq.com/@d3/color-legend
 * @param {*} param0 
 * @returns 
 */
export function colorLegendCont({
    color,
    title,
    tickSize = 2,
    width = 16 + tickSize,
    height = 250,
    marginTop = 1,
    marginRight = 0 + tickSize,
    marginBottom = 16,
    marginLeft = 0,
    ticks = height / 64,
    tickFormat,
    tickValues
} = {}) {
    const svg = d3.select("#legend")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .style("overflow", "visible")
        .style("display", "block");
    // .attr("transform", "translate(56,10)");

    let tickAdjust = g => g.selectAll(".tick line").attr("x1", -1.9 + marginRight - width);
    let x;

    // Continuous
    if (color.interpolate) {
        const n = Math.min(color.domain().length, color.range().length);

        x = color.copy().rangeRound(d3.quantize(d3.interpolate(marginLeft, width - marginRight), n));

        svg.append("image")
            .attr("x", marginLeft)
            .attr("y", marginTop)
            .attr("width", width - marginLeft - marginRight)
            .attr("height", height - marginTop - marginBottom)
            .attr("preserveAspectRatio", "none")
            .attr("xlink:href", ramp(color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))).toDataURL());
    }


    // Sequential
    else if (color.interpolator) {
        x = Object.assign(color.copy()
            .interpolator(d3.interpolateRound(marginTop, height - marginBottom)), {
            range() {
                return [marginTop, height - marginBottom];
            }
        });

        svg.append("image")
            .attr("x", marginLeft)
            .attr("y", marginTop)
            .attr("width", width - marginLeft - marginRight)
            .attr("height", height - marginTop - marginBottom)
            .attr("preserveAspectRatio", "none")
            .attr("xlink:href", ramp(color.interpolator()).toDataURL());

        // scaleSequentialQuantile doesn’t implement ticks or tickFormat.
        if (!x.ticks) {
            if (tickValues === undefined) {
                const n = Math.round(ticks + 1);
                tickValues = d3.range(n).map(i => d3.quantile(color.domain(), i / (n - 1)));
            }
            if (typeof tickFormat !== "function") {
                tickFormat = d3.format(tickFormat === undefined ? ",f" : tickFormat);
            }
        }
    }

    // // Threshold
    // else if (color.invertExtent) {
    //   const thresholds = color.thresholds ? color.thresholds() // scaleQuantize
    //     :
    //     color.quantiles ? color.quantiles() // scaleQuantile
    //     :
    //     color.domain(); // scaleThreshold

    //   const thresholdFormat = tickFormat === undefined ? d => d :
    //     typeof tickFormat === "string" ? d3.format(tickFormat) :
    //     tickFormat;

    //   x = d3.scaleLinear()
    //     .domain([-1, color.range().length - 1])
    //     .rangeRound([marginLeft, width - marginRight]);

    //   svg.append("g")
    //     .selectAll("rect")
    //     .data(color.range())
    //     .join("rect")
    //     .attr("x", (d, i) => x(i - 1))
    //     .attr("y", marginTop)
    //     .attr("width", (d, i) => x(i) - x(i - 1))
    //     .attr("height", height - marginTop - marginBottom)
    //     .attr("fill", d => d);

    //   tickValues = d3.range(thresholds.length);
    //   tickFormat = i => thresholdFormat(thresholds[i], i);
    // }

    // // Ordinal
    // else {
    //   y = d3.scaleBand()
    //     .domain(color.domain())
    //     .rangeRound([marginLeft, width - marginRight]);

    //   svg.append("g")
    //     .selectAll("rect")
    //     .data(color.domain())
    //     .join("rect")
    //     .attr("x", x)
    //     .attr("y", marginTop)
    //     .attr("width", Math.max(0, x.bandwidth() - 1))
    //     .attr("height", height - marginTop - marginBottom)
    //     .attr("fill", color);

    //   tickAdjust = () => {};
    // }

    svg.append("g")
        .attr("transform", `translate(${width}, 0)`)
        .call(d3.axisRight(x)
            .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
            .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
            .tickSize(tickSize)
            .tickValues(tickValues))
        .call(tickAdjust)
        .call(g => g.select(".domain").remove())
    // .call(g => g.append("text")
    //   .attr("x", marginLeft)
    //   .attr("y", marginTop + marginBottom - height - 6)
    //   .attr("fill", "currentColor")
    //   .attr("text-anchor", "start")
    //   .attr("font-weight", "bold")
    //   .text(title));

    return svg.node();
}

// function ramp(color, n = 256) {
//     var canvas = document.createElement('canvas');
//     canvas.width = n;
//     canvas.height = 1;
//     const context = canvas.getContext("2d");
//     for (let i = 0; i < n; ++i) {
//       context.fillStyle = color(i / (n - 1));
//       context.fillRect(i, 0, 1, 1);
//     }
//     return canvas;
//   }
export function ramp(interpolator, vertical = true) {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    if (vertical) {
        canvas.width = 1, canvas.height = 256;
        for (let i = 0; i < 256; ++i) {
            context.fillStyle = d3.rgb(interpolator(i / 255));
            context.fillRect(0, i, 1, 1);
        }
    } else {
        canvas.width = 256, canvas.height = 1;
        for (let i = 0; i < 256; ++i) {
            context.fillStyle = d3.rgb(interpolator(i / 255));
            context.fillRect(i, 0, 1, 1);
        }
    }
    return canvas;
}
