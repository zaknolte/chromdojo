import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, ALL, Patch, callback, no_update, clientside_callback, ClientsideFunction
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import numpy as np

calibration_panel = dmc.TabsPanel(
    html.Div(
        [
            html.Div(
                [
                    dcc.Dropdown(id="peak-calibration-selection", clearable=False, className="dark-dropdown"),
                    html.Div(
                        [
                            dbc.Button("Add Calibrator", id="add-cal", color="success", className="me-1", style={"width": "100%"}, disabled=True),
                            dag.AgGrid(
                                id="calibration-table",
                                columnDefs=[
                                    {
                                        "field": "Level",
                                        "width": 80,
                                        "resizable": False,
                                        "sortable": False,
                                        "suppressMovable": True,
                                    },
                                    {
                                        "field": "Concentration",
                                        "width": 100,
                                        "resizable": False,
                                        "sortable": False,
                                        "suppressMovable": True,
                                        'editable': True,
                                        'cellStyle': {
                                            "display": "flex",
                                            "justifyContent": "end"
                                        }
                                    },
                                    {
                                        "field": "Abundance",
                                        "width": 100,
                                        "resizable": False,
                                        "sortable": False,
                                        "suppressMovable": True,
                                        'editable': True,
                                        'cellStyle': {
                                            "display": "flex",
                                            "justifyContent": "end"
                                        }
                                    },
                                    {
                                        "field": "Use",
                                        "width": 45,
                                        "resizable": False,
                                        "sortable": False,
                                        "suppressMovable": True,
                                        "cellRenderer": "Checkbox",
                                        "cellStyle": {"textAlign": "center"}
                                    },
                                    {
                                        "field": "Delete",
                                        "width": 70,
                                        "resizable": False,
                                        "sortable": False,
                                        "suppressMovable": True,
                                        "cellRenderer": "deleteCal",
                                        "cellRendererParams": {
                                            "variant": "subtle",
                                            "icon": "material-symbols-light:cancel-outline",
                                            "color": "red",
                                        },
                                        'cellStyle': {
                                            "display": "flex",
                                            "alignItems": "center"
                                        }
                                    },
                                ],
                                style={"width": 400, "height": 400},
                                className="ag-theme-balham-dark"
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Regression"),
                                    dbc.Select(
                                        id="regression-select",
                                        value="linear",
                                        options=[
                                            {"value": "linear", "label": "Linear"},
                                            {"value": "quadratic", "label": "Quadratic"},
                                            {"value": "response-factor", "label": "Response Factor"},
                                        ],
                                        style={"width": 200}
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.H6("Weighting"),
                                    dbc.Select(
                                        id="weight-select",
                                        value="none",
                                        options=[
                                            {"value": "none", "label": "None"},
                                            # {"value": "1x", "label": "1/x"},
                                            # {"value": "1x2", "label": "1/x^2"},
                                            # {"value": "1y", "label": "1/y"},
                                            # {"value": "1y2", "label": "1/y^2"},
                                        ],
                                        style={"width": 200}
                                    ),
                                ],
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-evenly", "margin-bottom": "-10%", "position": "relative", "zIndex": 10}
                    ),
                    dcc.Graph(
                        figure=go.Figure(
                            go.Scatter(
                                x=[0],
                                y=[0]
                            ),
                            layout={
                                'paper_bgcolor': 'rgba(0,0,0,0)',
                                "showlegend": False,
                                "xaxis": {
                                    "color": "white",
                                    "title": {
                                        "text": "Concentration"
                                    },
                                    "showgrid": False
                                },
                                "yaxis": {
                                    "color": "white",
                                    "title": {
                                        "text": "Abundance",
                                    },
                                    "showgrid": False
                                }
                            },
                        ),
                        id="calibration-curve",
                        config={
                            "displayModeBar": False,
                            "staticPlot": True
                        },
                        style={"height": 550}
                    )
                ]
            )
        ],
        style={"display": "flex"}
    ),
    value="curves"
)

@callback(
    Output("peak-calibration-selection", "options"),
    Input("add-peak", "n_clicks"),
    Input({'type': 'peak-edit-name', 'index': ALL}, "value"),
    prevent_initial_call=True
)
def add_curve_options(new_peak, edited_peak):
    return [peak for peak in edited_peak]

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='updateTable'
    ),
    Output("calibration-table", "rowData", allow_duplicate=True),
    Output("add-cal", "disabled"),
    Output("table-updates", "data", allow_duplicate=True),
    Output("regression-select", "value"),
    Output("weight-select", "value"),
    Input("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='addCal'
    ),
    Output("calibration-table", "rowData", allow_duplicate=True),
    Input("add-cal", "n_clicks"),
    State("peak-calibration-selection", "value"),
    State("calibration-table", "rowData"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='deleteCal'
    ),
    Output("table-updates", "data", allow_duplicate=True),
    Output("calibration-table", "rowData", allow_duplicate=True),
    Input("calibration-table", "cellRendererData"),
    State("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='updateCal'
    ),
    Output("table-updates", "data", allow_duplicate=True),
    Input("calibration-table", "cellValueChanged"),
    Input("results-table", "cellValueChanged"),
    State("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='updateCalType'
    ),
    Output("table-updates", "data", allow_duplicate=True),
    Input("regression-select", "value"),
    State("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='updateCalWeight'
    ),
    Output("table-updates", "data", allow_duplicate=True),
    Input("weight-select", "value"),
    State("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace="calibration",
        function_name='updateCoefs'
    ),
    Output("table-updates", "data", allow_duplicate=True),
    Input("calibration-intermediate", "data"),
    State("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)

@callback(
    Output("calibration-curve", "figure", allow_duplicate=True),
    Output("calibration-intermediate", "data", allow_duplicate=True),
    Input("table-updates", "data"),
    State("peak-calibration-selection", "value"),
    State("x-y-data", "data"),
    prevent_initial_call=True,
)
def update_calibrators(_, compound, peak_data):
    def get_r_squared(coefs):
        fit = np.poly1d(coefs)
        yhat = fit(x)
        ybar = np.sum(y)/len(y)
        ssreg = np.sum((yhat-ybar)**2)
        sstot = np.sum((y - ybar)**2)
        return ssreg / sstot

    patched_fig = Patch()
    coefs = []
    if peak_data is None:
        patched_fig["layout"]["annotations"] = None
        patched_fig["data"] = [go.Scatter(x=[0], y=[0], mode="markers")]
        return patched_fig, coefs
    
    for peak in peak_data["peaks"]:
        if not peak["calibration"]["points"]:
            patched_fig["layout"]["annotations"] = None
            patched_fig["data"] = [go.Scatter(x=[0], y=[0], mode="markers")]
            return patched_fig, coefs
        
        if peak["name"] == compound:
            traces = []
            x = []
            x_total = []
            y = []
            # build cal points
            for cal in peak["calibration"]["points"]:
                if cal["used"]:
                    marker = {
                        "symbol": "circle",
                        "line": {
                            "color": "rgb(0, 0, 0)"
                        },
                        "color": "rgb(50, 50, 50)"
                    }
                    x.append(cal["x"])
                    y.append(cal["y"])
                else:
                    marker = {
                        "symbol": "circle-open",
                        "line": {
                            "color": "rgb(0, 0, 0)"
                        },
                        "color": "rgb(50, 50, 50)"
                    }
                x_total.append(cal["x"])

                traces.append(go.Scatter(x=[cal["x"]], y=[cal["y"]], mode="markers", marker=marker))

            
            text = "y = "
            x = np.asarray(x)
            y = np.asarray(y)

            weights = {
                "none": None,
                "1x": 1 / x,
                "1x2": 1 / (x * x),
                "1y": 1 / y,
                "1y2": 1 / (y * y),
            }

            w = weights[peak["calibration"]["weighting"]]
            # build curves
            try:
                if peak["calibration"]["type"] == "linear":
                    coefs = np.polyfit(x, y, 1)
                    r2 = get_r_squared(coefs)
                    # add additional points to plot a smoother curve
                    x_fit = np.linspace(np.min(x_total), np.max(x_total), 20)

                    y_fit = coefs[0] * x_fit + coefs[1]

                    const_sign = "+" if coefs[1] > 0 else ""

                    text += f"{coefs[0]:.4g}x {const_sign} {coefs[1]:.4g}"

                elif peak["calibration"]["type"] == "quadratic":
                    coefs = np.polyfit(x, y, 2)
                    r2 = get_r_squared(coefs)
                    # add additional points to plot a smoother curve
                    x_fit = np.linspace(np.min(x_total), np.max(x_total), 20)
                    y_fit = (coefs[0] * x_fit * x_fit) + (coefs[1] * x_fit) + coefs[2]

                    slope_sign = "+" if coefs[1] > 0 else ""
                    const_sign = "+" if coefs[2] > 0 else ""

                    text += f"{coefs[0]:.4g}x^2 {slope_sign} {coefs[1]:.4g}x {const_sign} {coefs[2]:.4g}"

                elif peak["calibration"]["type"] == "response-factor":
                    # if "x" in peak["calibration"]["weighting"]:
                    #     pass 
                    coefs = np.linalg.lstsq(np.asarray(x).reshape(-1,1), y)[0]
                    # add additional points to plot a smoother curve
                    x_fit = np.linspace(np.min(x_total), np.max(x_total), 20)
                    y_fit = x_fit * coefs[0]

                    text += f"{coefs[0]:.4g}x"

                if peak["calibration"]["type"] != "response-factor":
                    text += f"<br>r2 = {r2:.5f}"

            except Exception:
                coefs = []


            annotation = [
                {
                    "text": text,
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.07,
                    "y": 0.95,
                    "showarrow": False,
                    "textfont": {
                        "color": "darkgrey"
                    }
                }
            ]

            traces.append(
                go.Scatter(
                    x=x_fit,
                    y=y_fit,
                    mode="lines",
                    marker={"color": "darkgrey"},
                )
            )

            patched_fig["layout"]["annotations"] = annotation
            patched_fig["layout"]["xaxis"]["title"]["text"] = f"Concentration ({peak['calibration']['units']})"
            patched_fig["data"] = traces
    
            return patched_fig, coefs
    return no_update, coefs