window.dash_clientside = Object.assign({}, window.dash_clientside, {
    graph: {
        renderGraph: function(data) {
            if(typeof data !== "undefined") {
                var plot = [{
                    x: data.x,
                    y: data.y,
                    type: 'scatter'
                }];
                return {
                    "data": plot,
                    "layout": {
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        "showlegend": false,
                        "xaxis": {
                            "color": "white",
                            "title": {
                                "text": "Time",
                            },
                            "showgrid": false
                        },
                        "yaxis": {
                            "color": "white",
                            "title": {
                                "text": "Abundance",
                            },
                            "showgrid": false
                        }
                    },
                };
            };
            return window.dash_clientside.no_update;
        }
    }
});