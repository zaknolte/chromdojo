function initializeY(size) {
    return Array(size).fill(0);
};

function add_bleed(y, start, stop, height, factor) {
    // x range to replace with slope
    var x = [];
    for (let i = 0; i < stop - start + 1; i++) {
      x.push(i / 60);
    };
    
    // shift range to center on 0 for sigmoid
    for (i = 0; i < x.length; i++) {
        x[i] -= x[Math.floor(x.length / 2)];
    };

    var vals = x.map((num) => {
        return height / (1 + Math.exp(-num*factor) / factor);
    });

    for (let i = start; i <= stop + 1; i++) {
        y[i] += vals[i]
    };

    for (let i = stop + 1; i < y.length; i++) {
        y[i] += vals[vals.length - 1]
    };

    return y;
};

function add_trendline(y, start, stop, factor, reset) {
    if (factor != 0) {
        var ySlice = y.slice(start, stop);

        for (let i = 0; i < ySlice.length; i++) {
            ySlice[i] += (i * factor);
        };

        for (let i = 0; i < stop - start; i++) {
            y[i + start] += ySlice[i];
        };

        if (!reset) {
            for (let i = stop; i < y.length; i++) {
                y[i] += ySlice[ySlice.length - 1];
            };
        };
    };

    return y;
};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    options: {
        updateBaseline: function(
            noise,
            baselineShift,
            isBleed,
            baselineStarts,
            baselineStops,
            slopeFactors,
            resetBaseline,
            deleteTrendline,
            bleedStart,
            bleedStop,
            bleedHeight,
            bleedSlope,
            peaksUpdated,
            data
        ) {
            console.log(peaksUpdated);
            if(typeof data !== "undefined") {
                console.log(data)
                // start fresh with Y of zeros of size x
                var y = initializeY(data["x"].length);

                // add y values from every peak
                data["peaks"].forEach((peak) => {
                    var peakY = peak.create_peak(data["x"]);
                    y = y.map((num, idx) => {return num + peakY[idx]});
                });

                if (isBleed){
                    // add y values from column bleed options
                    y = add_bleed(y, bleedStart[0] * 60, bleedStop[0] * 60, bleedHeight[0], bleedSlope[0] * 60);
                } else{
                    // add y values from baseline trends
                    for (let i = 0; i < baselineStarts.length; i++) {
                        y = add_trendline(y, baselineStarts[i] * 60, baselineStops[i] * 60, slopeFactors[i] / 60, resetBaseline[i]);
                    };
                };
                
                if (noise) {
                    y = y.map((num, i) => {return num += noise[i]})
                };

                return {"x": data["x"], "y": y, "peaks": data["peaks"]};
            };
            return window.dash_clientside.no_update;
        }
    }
});
