function calcX(numPoints) {
    var arr = [];
    for (var i = 0; i < numPoints + 1; i++) {
      arr.push(i / 60);
    }
    return arr;
  }

class Compound {
  constructor(name, x, center, height, width, skew) {
      this.name = name;
      this.x = x;
      this.height = height;
      this.center = center;
      this.width = width;
      this.skew = skew;
      this.area = 0;
      this.start_idx = 0;
      this.stop_idx = 0;
      this.concentration = 0;
      this.unit = "ppm";
      this.calibration = new Calibration();
  }

  create_peak() {
      // current formula with skewness does not draw with width = 0
      // set to minimal sharp value to improve UX and not have peaks disappearing
      if (this.width === 0) {
          this.width = 0.01;
      }
      // https://www.desmos.com/calculator/gokr63ciym
      return this.height * np.exp(-0.5 * ((this.x - this.center) / (this.width + (this.skew * (this.x - this.center))))**2);
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
    clientside: {
        add_peaks: function(numPoints, names, centers, heights, widths, skews, data) {
            console.log(names)
            console.log(data)
            var x = calcX(numPoints)
            var peak = new Compound(names[0], x, centers[0], heights[0], widths[0], skews[0]);
            return peak;
        }
    }
});