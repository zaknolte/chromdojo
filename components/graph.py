import plotly.graph_objects as go
from dash import dcc, callback, Output, Input, State, Patch, ALL, no_update, ctx, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import numpy as np
import peakutils
from scipy.signal import find_peaks
from components.Compound import Compound
import jsonpickle

def make_annotations(peaks, annotations_options):
    annotations = []
    for peak in peaks:
        text = ""
        for option in annotations_options:
            if option["Field"] == "Peak Name" and option["Add to Plot"]:
                text += f"{peak['name']}<br>"
            if option["Field"] == "RT" and option["Add to Plot"]:
                text += f"RT: {peak['center']:.2f} min<br>"
            if option["Field"] == "Concentration" and option["Add to Plot"]:
                text += f"Conc: {peak['concentration']:.2f} {peak['calibration']['units']}<br>" #TODO add integration concentrations
            if option["Field"] == "Area" and option["Add to Plot"]:
                text += f"Area: {peak['area']:.2f}<br>"
            if option["Field"] == "Height" and option["Add to Plot"]:
                text += f"Height: {peak['height']:.2f}<br>"
        annotations.append(
            {
                "text": text,
                "x": peak['center'],
                "y": peak['height'] * 1.04,
                "height": 120,
            }
        )

    return annotations

def integrate_peaks(peak_list, x, y, width, height, threshold, distance, prominence, wlen):
    x = np.asarray(x)
    y = np.asarray(y)
    initial_peaks = peak_list
    try:
        peaks = find_peaks(y, width=width, height=height, threshold=threshold, distance=distance, prominence=prominence, wlen=wlen)
        baseline = peakutils.baseline(y)
        for i in range(len(peaks[1]["left_bases"])):
            for peak in peak_list:
                if peak["center"] == peaks[0][i] / 60:
                    clear_integration(peak)
                    start, stop = peaks[1]["left_bases"][i], peaks[1]["right_bases"][i]
                    auc = np.trapz(y[start:stop], x[start:stop]) - np.trapz(baseline[start:stop], x[start:stop])
                    peak["start_idx"] = start
                    peak["stop_idx"] = stop
                    peak["area"] = auc

        return peak_list
    except ZeroDivisionError:
        return initial_peaks

def clear_integration(peak):
    peak["start_idx"] = 0
    peak["stop_idx"] = 0
    peak["area"] = 0

fig = go.Figure(
        go.Scatter(
            x=[i for i in range(18)],
            y=[0 for i in range(18)],
            mode='lines'
        ),
        layout={
            'paper_bgcolor': 'rgba(0,0,0,0)',
            "showlegend": False,
            "xaxis": {
                "color": "white",
                "title": {
                    "text": "Time",
                },
                "showgrid": False
            },
            "yaxis": {
                "color": "white",
                "title": {
                    "text": "Abundance",
                },
                "showgrid": False,
            }
        },
)

configs = {
    "scrollZoom": True,
    "modeBarButtons": [["pan2d", "zoom2d", "drawline", "resetScale2d"]],
    "displayModeBar": True,
}

graph = dcc.Graph(
    figure=fig, 
    id="main-fig", 
    config=configs, 
    style={"height": 800}
)

clientside_callback(
    ClientsideFunction(
        namespace="peaks",
        function_name='xyData'
    ),
    Output("x-y-data", "data"),
    Input("graph-datapoints", "value"),
    Input("peak-added", "data"),
    Input({'type': 'peak-edit-name', 'index': ALL}, "value"),
    Input({"type": "peak-center", "index": ALL}, "value"),
    Input({"type": "peak-height", "index": ALL}, "value"),
    Input({"type": "peak-width", "index": ALL}, "value"),
    Input({"type": "peak-skew", "index": ALL}, "value"),
    Input({"type": "peak-delete", "index": ALL}, "n_clicks"),
    Input("noise-data", "data"),
    Input("baseline-shift", "value"),
    Input("trendline-choice", "checked"),
    Input({"type": "baseline-start", "index": ALL}, "value"),
    Input({"type": "baseline-stop", "index": ALL}, "value"),
    Input({"type": "baseline-slope", "index": ALL}, "value"),
    Input({"type": "reset_baseline", "index": ALL}, "value"),
    Input({"type": "trendline-delete", "index": ALL}, "n_clicks"),
    Input({"type": "bleed-start", "index": ALL}, "value"),
    Input({"type": "bleed-stop", "index": ALL}, "value"),
    Input({"type": "bleed-height", "index": ALL}, "value"),
    Input({"type": "bleed-slope", "index": ALL}, "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="peaks",
        function_name='addIntegration'
    ),
    Output("integration-intermediate", "data"),
    Input("integration-data", "data"),
    State("x-y-data", "data"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="graph",
        function_name='renderGraph'
    ),
    Output("main-fig", "figure", allow_duplicate=True),
    Input("annotations-options", "virtualRowData"), # trigger for re-arranging annotation rows
    Input("annotations-options", "cellRendererData"), # trigger for annotation checkboxes
    Input("annotations-options", "cellClicked"), # trigger for clicking a cell that contains a checkbox (cell clicks check box but don't trigger checkbox callback)
    Input("integration-intermediate", "data"),
    Input("calibration-intermediate", "data"),
    Input("x-y-data", "data"),
    State("baseline-shift", "value"),
    prevent_initial_call=True
)

@callback(
    Output("integration-data", "data"),
    Input("auto-integration", "checked"),
    Input("integration-width", "value"),
    Input("integration-height", "value"),
    Input("integration-threshold", "value"),
    Input("integration-distance", "value"),
    Input("integration-prominence", "value"),
    Input("integration-wlen", "value"),
    # Input("main-fig", "relayoutData"), # shapes trigger relayout
    # Input("table-updates", "data"), # make sure to update fig after minor updates to cals / results table
    Input("x-y-data", "data"),
    prevent_initial_call=True
)
def add_integrations(
    auto_integrate,
    integration_width,
    integration_height,
    integration_threshold,
    integration_distance,
    integration_prominence,
    integration_wlen,
    # manual_integrations,
    # table_updates
    peak_data,
    ):
    if peak_data:
        # clear out any existing integrations and recalculate based on updated parameters
        for peak in peak_data["peaks"]:
            clear_integration(peak)
        if auto_integrate:
            integrations = integrate_peaks(peak_data["peaks"], peak_data["x"], peak_data["y"], integration_width, integration_height, integration_threshold, integration_distance, integration_prominence, integration_wlen)
        else:
            integrations = peak_data["peaks"]
            
        return integrations
    return no_update
