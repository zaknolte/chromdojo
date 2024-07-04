function calcX(numPoints) {
    var arr = [];
    for (var i = 0; i < numPoints + 1; i++) {
      arr.push(i / 60);
    }
    return arr;
}

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
  }

  create_peak(x) {
    // current formula with skewness does not draw with width = 0
    // set to minimal sharp value to improve UX and not have peaks disappearing
    if (this.width === 0) {
        this.width = 0.01;
    }
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
  

  }
  clear_integration() {
    this.area = 0;
    this.start_idx = 0;
    this.stop_idx = 0;
  }
};

class Calibration {
  constructor() {
    this.points = [];
    this.type = null;
    this.weighting = null;
    this.coefficients = [];
    this.units = "ppm";
  }

  add_point(point) {
    this.points.append(point);
    this.sort_points();
  }

  delete_point(level) {
    for (let index = this.points.length - 1; index >= 0; --index) {
        if (this.points[index].name === level) {
            delete this.points[index];
        }
    }
    this.sort_points();
  }

  rename_points() {
    this.sort_points();
    this.points = this.points.map((x, i) => x.name = i);
  }

  sort_points() {
    this.points.sort((a, b) => a.name.localeCompare(b.name));
  }

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
    }

    return 0;
  }
}

class calPoint {
  constructor(name, x, y) {
    this.name = name;
    this.x = x;
    this.y = y;
    this.used = True;
  }

  set_used(use) {
    this.used = use;
  }
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    peaks: {
        addPeak: function(numPoints, n_clicks, names, centers, heights, widths, skews, data) {
            // First initial peak added - no data yet
            if(typeof data === "undefined") {
                var x = calcX(numPoints)
                var peak = new Compound(names[0], n_clicks, centers[0], heights[0], widths[0], skews[0])
                return {"x": x, "y": peak.create_peak(x), "peaks": [peak]};
            } else {
                data["peaks"].push(new Compound(names[names.length-1], n_clicks, centers[centers.length-1], heights[heights.length-1], widths[widths.length-1], skews[skews.length-1]));
            }
            return {"x": data["x"], "y": data["y"], "peaks": data["peaks"]};
        },
        
        deletePeak: function(is_deleted, vals, data) {
            var remainingIdx = [];
            var remainingPeaks = [];
            // component gets removed in python callback function
            // grab a list of components that still exist and rebuild peaks remaining
            for (ctx of dash_clientside.callback_context.states_list) {
                try {
                    for (vals of ctx) {
                        remainingIdx.push(vals.id.index)
                    }
                } catch (error) {
                }
            }
            // rebuild peaks using only component idx that still exist
            for (peak of data["peaks"]) {
                if (remainingIdx.includes(peak.idx)) {
                    remainingPeaks.push(peak);
                }
            };
            return {"x": data["x"], "y": data["y"], "peaks": remainingPeaks};
        },
        
        updatePeak: function(names, centers, heights, widths, skews, data) {
            if(typeof data !== "undefined") {
                var y = Array(data["x"].length).fill(0);
                const ctx_idx = dash_clientside.callback_context.triggered_id.index
                data["peaks"].forEach((peak) => {
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
                    }
                    peakY = peak.create_peak(data["x"]);
                    y = y.map((num, idx) => {return num + peakY[idx]});
                });
                return {"x": data["x"], "y": y, "peaks": data["peaks"]};
            }
        }
    }
});