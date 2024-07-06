function calcX(numPoints) {
    var arr = [];
    for (let i = 0; i < numPoints + 1; i++) {
      arr.push(i / 60);
    }
    return arr;
};

function add_bleed(y, start, stop, height, factor) {
    // x range to replace with slope
    var x = [];
    for (let i = 0; i < stop - start + 1; i++) {
      x.push(i / 60);
    };
    
    // shift range to center on 0 for sigmoid
    var mid = Math.max(...x) / 2
    for (i = 0; i < x.length; i++) {
        x[i] -= mid;
    };
    // calculate sigmoid
    var vals = x.map((num) => {
        return height / (1 + Math.exp(-num*factor) / factor);
    });
    // update sliced values
    for (let i = 0; i < stop - start + 1; i++) {
        y[i + start] += vals[i]
    };
    // update values after stop
    for (let i = stop + 1; i < y.length; i++) {
        y[i] = vals[vals.length - 1]
    };

    return y;
};

function add_trendline(y, start, stop, factor, reset) {
    if (factor != 0) {
        var ySlice = y.slice(start, stop);
        // calculate slope
        for (let i = 0; i < ySlice.length; i++) {
            ySlice[i] += (i * factor);
        };
        // add slope
        for (let i = 0; i < stop - start; i++) {
            y[i + start] += ySlice[i];
        };
        // set values after stop to same as end of slope
        if (!reset) {
            for (let i = stop; i < y.length; i++) {
                y[i] += ySlice[ySlice.length - 1];
            };
        };
    };

    return y;
};

class Compound {
    constructor(name, idx, center, height, width, skew) {
        this.name = name;
        this.idx = idx;
        this.height = height;
        this.center = center;
        this.width = width;
        this.skew = skew;
        this.area = 0;
        this.start_idx = 0;
        this.stop_idx = 0;
        this.concentration = 0;
        this.calibration = new Calibration();
    };

    create_peak(x) {
        // current formula with skewness does not draw with width = 0
        // set to minimal sharp value to improve UX and not have peaks disappearing
        if (this.width === 0) {
            this.width = 0.01;
        };
        // https://www.desmos.com/calculator/gokr63ciym
        var y = Array(x.length).fill(0);
        var calcY = y.map((num, idx) => {
            return this.height * Math.exp(-0.5 * ((x[idx] - this.center) / (this.width + (this.skew * (x[idx] - this.center))))**2);
            // this.height * Math.exp(-0.5 * ((x[idx] - this.center) / (this.width + (this.skew * (x[idx] - this.center))))**2)
        });
        return calcY;
        // https://www.desmos.com/calculator/k5y9glwjee   ??
        // https://math.stackexchange.com/questions/3605861/what-is-the-graph-function-of-a-skewed-normal-distribution-curve
        // https://cremerlab.github.io/hplc-py/methodology/fitting.html
    

    };
    clear_integration() {
        this.area = 0;
        this.start_idx = 0;
        this.stop_idx = 0;
    };
    calculate_concentration() {
        this.concentration = this.calibration.calculate_concentration(this.area)
    }
};

class Calibration {
  constructor() {
    this.points = [];
    this.type = null;
    this.weighting = null;
    this.coefficients = [];
    this.units = "ppm";
  };

  addPoint(point) {
    this.points.push(point);
  };

  deletePoint(level) {
    this.points = this.points.filter((x) => x.name !== level)
  };

  renamePoints() {
    this.points = this.points.map((point, i) => ({
        name: i + 1,
        x: point.x,
        y: point.y,
        used: point.used
    }));
  };

  setPointsUsed(idx, value) {
    this.points[idx].used = value;
  };

  setPointsX(idx, value) {
    this.points[idx].x = value;
  };

  setPointsY(idx, value) {
    this.points[idx].y = value;
  };

  calculate_concentration(area) {
    if (!this.type || this.coefficients.every((i) => false)) {
        return 0;
    }
    else if (this.type === "linear") {
        return this.coefficients[0] * area + this.coefficients[1];
    }
    else if (this.type === "quadratic") {
        return (this.coefficients[0] * area * area) + (this.coefficients[1] * area) + this.coefficients[2];
    }
    else if (this.type === "response-factor") {
        return this.coefficients[0] * area;
    };

    return 0;
  };
};

class calPoint {
  constructor(name, x, y) {
    this.name = name;
    this.x = x;
    this.y = y;
    this.used = true;
  };
};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    // peak namespace functions
    peaks: {
        xyData: function(
            numPoints,
            peakAdded,
            names,
            centers,
            heights,
            widths,
            skews,
            peakDeleted,
            noise,
            baselineShift,
            isBleed,
            baselineStarts,
            baselineStops,
            slopeFactors,
            resetBaseline,
            trendlineDeleted,
            bleedStart,
            bleedStop,
            bleedHeight,
            bleedSlope,
            data,
        ) {
            // First initial peak added - no data yet
            if(typeof data == "undefined") {
                var triggered = dash_clientside.callback_context.triggered
                if (triggered[triggered.length - 1]["prop_id"] == "peak-added.data" && triggered[triggered.length - 1]["value"] == 1) {
                    var x = calcX(numPoints);
                    var peak = new Compound(names[0], peakAdded, centers[0], heights[0], widths[0], skews[0]);
                    return {"x": x, "y": peak.create_peak(x), "peaks": [peak]};
                };
                return window.dash_clientside.no_update;
            } else {
                // component gets removed in python callback function
                // grab a list of components that still exist and rebuild peaks remaining
                var y = data["y"];
                var remainingIdx = [];
                for (ctx of dash_clientside.callback_context.inputs_list) {
                    if (ctx instanceof Array) {
                        for (vals of ctx) {
                            if (vals.id.type === "peak-delete") {
                                remainingIdx.push(vals.id.index);
                            }
                        }
                    }
                }
                // check if new peak was created and add it
                if (remainingIdx.length > data.peaks.length) {
                    data.peaks.push(new Compound(names[names.length-1], peakAdded, centers[centers.length-1], heights[heights.length-1], widths[widths.length-1], skews[skews.length-1]));
                    remainingIdx.push(peakAdded);
                }
                // rebuild peaks using only component idx that still exist
                var remainingPeaks = [];
                for (peak of data.peaks) {
                    if (remainingIdx.includes(peak.idx)) {
                        remainingPeaks.push(peak);
                    };
                };
                // begin calculating y values for all remaining peaks
                try {
                    var peakEdits = ["peak-edit-name", "peak-center", "peak-height", "peak-width", "peak-skew"]
                    if (peakEdits.includes(dash_clientside.callback_context.triggered_id.type)) {
                        const ctx_idx = dash_clientside.callback_context.triggered_id.index;
                        remainingPeaks.forEach((peak) => {
                            if (peak.idx === ctx_idx) {
                                switch (dash_clientside.callback_context.triggered_id.type) {
                                    case "peak-edit-name":
                                        peak.name = dash_clientside.callback_context.triggered[0].value;
                                        break;
                                    case "peak-center":
                                        peak.center = dash_clientside.callback_context.triggered[0].value;
                                        break;
                                    case "peak-height":
                                        peak.height = dash_clientside.callback_context.triggered[0].value;
                                        break;
                                    case "peak-width":
                                        peak.width = dash_clientside.callback_context.triggered[0].value;
                                        break;
                                    case "peak-skew":
                                        peak.skew = dash_clientside.callback_context.triggered[0].value;
                                        break;
                                };
                            };
                        });
                    };
                } catch (error) {
                };
                // start fresh with y and recalc all values
                y = Array(data["x"].length).fill(0);
                // make sure to calculate trendline data first as they can be multiplicative to existing y data
                if (isBleed){
                    // add y values from column bleed options
                    y = add_bleed(y, bleedStart[0] * 60, bleedStop[0] * 60, bleedHeight[0], bleedSlope[0] * 60);
                } else{
                    // add y values from baseline trends
                    for (let i = 0; i < baselineStarts.length; i++) {
                        y = add_trendline(y, baselineStarts[i] * 60, baselineStops[i] * 60, slopeFactors[i] / 60, resetBaseline[i]);
                    };
                };
                // add noise
                if (noise) {
                    y = y.map((num, i) => {return num += noise[i]});
                };
                // add baseline shift
                if (baselineShift) {
                    y = y.map((num) => {return num += baselineShift});
                };
                // add y values from every peak
                remainingPeaks.forEach((peak) => {
                    var peakY = peak.create_peak(data["x"]);
                    peak.clear_integration();
                    y = y.map((num, idx) => {return num + peakY[idx]});
                });
                return {"x": data["x"], "y": y, "peaks": remainingPeaks};
            };
        },
    },
    // graph namespace functions
    graph: {
        renderGraph: function(options, isChecked, isClicked, integrationData, data, autoIntegrate) {
            if(typeof data !== "undefined") {
                var annotations = [];
                // main x y plot
                var plot = [{
                    x: data.x,
                    y: data.y,
                    type: 'scatter'
                }];
                for (peak of data.peaks) {
                    // clear out integrations and rebuild
                    peak.clear_integration();
                    if (autoIntegrate) {
                        for (integration of integrationData) {
                            if (integration.idx === peak.idx) {
                                peak.area = integration.area;
                                peak.start_idx = integration.start_idx;
                                peak.stop_idx = integration.stop_idx;
                            };
                        };
                    }

                    if (peak.area > 0) {
                        // add integration shapes
                        plot.push({
                            x: data.x.slice(peak.start_idx, peak.stop_idx),
                            y: data.y.slice(peak.start_idx, peak.stop_idx),
                            type: 'scatter',
                            mode: 'lines',
                            fill: 'toself'
                        });
                    };
                    // add annotations
                    var text = '';
                    for (option of options) {
                        if (option['Field'] === 'Peak Name' && option['Add to Plot']) {
                            text += `${peak.name}<br>`
                        };
                        if (option['Field'] === 'RT' && option['Add to Plot']) {
                            text += `RT: ${peak.center.toFixed(2)} min<br>`
                        };
                        if (option['Field'] === 'Concentration' && option['Add to Plot']) {
                            text += `Conc: ${peak.calibration.calculate_concentration(peak.area).toFixed(2)} ${peak.calibration.units}<br>`
                        };
                        if (option['Field'] === 'Area' && option['Add to Plot']) {
                            text += `Area: ${peak.area.toFixed(2)}<br>`
                        };
                        if (option['Field'] === 'Height' && option['Add to Plot']) {
                            text += `Height: ${peak.height.toFixed(2)}<br>`
                        };
                    };
                    annotations.push({
                        text: text,
                        x: peak.center,
                        y: peak.height * 1.1,
                        height: 150,
                        showarrow: false
                    });
                };
                return {
                    data: plot,
                    layout: {
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        showlegend: false,
                        xaxis: {
                            color: "white",
                            title: {
                                text: "Time",
                            },
                            showgrid: false
                        },
                        yaxis: {
                            color: "white",
                            title: {
                                text: "Abundance",
                            },
                            showgrid: false,
                        },
                        annotations: annotations
                    },
                };
            };
            return window.dash_clientside.no_update;
        }
    },
    calibration: {
        updateTable: function(compound, data) {
            if(typeof data !== "undefined") {
                var rowData = [];
                for (peak of data.peaks) {
                    if (peak.name === compound) {
                        for (cal of peak.calibration.points) {
                            rowData.push({
                                Level: cal.name,
                                Concentration: cal.x,
                                Abundance: cal.y,
                                Use: cal.used,
                                Delete: "X"
                            });
                        };
                    };
                };
                return [rowData, false];
            };
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        },
        addCal: function(n_clicks, compound, tableData, peakData) {
            if(typeof peakData !== "undefined") {
                var rowData = [...tableData]
                for (peak of peakData.peaks) {
                    if (peak.name === compound) {
                        let name = peak.calibration.points.length + 1
                        rowData.push({
                            Level: name,
                            Concentration: 0,
                            Abundance: 0,
                            Use: true,
                            Delete: "X"
                        });
                        peak.calibration.addPoint(new calPoint(name, 0, 0));
                        return rowData;
                    };
                };
            };
            return window.dash_clientside.no_update;
        },
        deleteCal: function(event, compound, data) {
            if(typeof data !== "undefined") {
                var rowData = [];
                for (peak of data.peaks) {
                    if (peak.name === compound) {
                        if (event.colId === "Delete") {
                            peak.calibration.deletePoint(event.rowIndex + 1);
                            peak.calibration.renamePoints();
                            for (cal of peak.calibration.points) {
                                rowData.push({
                                    Level: cal.name,
                                    Concentration: cal.x,
                                    Abundance: cal.y,
                                    Use: cal.used,
                                    Delete: "X"
                                });
                            };
                            return [new Date(), rowData];
                        };
                    };
                };
            };
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        },
        updateCal: function(event, regression, weighting, unitChange, compound, data) {
            if(typeof data !== "undefined") {
                for (peak of data.peaks) {
                    if (peak.name === compound) {
                        for (cal of peak.calibration.points) {
                            if (event[0].colId === "Use") {
                                peak.calibration.setPointsUsed(event[0].rowIndex, event[0].value);
                            } else if (event[0].colId === "Concentration") {
                                peak.calibration.setPointsX(event[0].rowIndex, event[0].value);
                            } else if (event[0].colId === "Abundance") {
                                peak.calibration.setPointsY(event[0].rowIndex, event[0].value);
                            }
                        };
                        peak.calibration.type = regression;
                        peak.calibration.weighting = weighting;
                    };
                };
                return new Date();
            };
            return window.dash_clientside.no_update;
        }
    }
});