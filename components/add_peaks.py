from dash import dcc, html, Input, Output, ALL, Patch, callback, MATCH, ctx, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# base peak accordion - no peaks exist by default
peak_accordian = dmc.Accordion(
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Peaks",
                    icon=DashIconify(
                        icon="fa-brands:think-peaks",
                        color="black",
                        width=20,
                    ),
                ),
                dmc.AccordionPanel(
                    [
                        dbc.Button("+ Add Peak", id="add-peak", style={"width": "100%"}),
                        html.Hr(),
                        html.Div(id="add-peak-container")
                    ],
                    id="add-peak-accordian"
                ),
            ],
            value="peak-accordian",
        ),
        # clientside callbacks trigger before dash python callbacks
        # force python callback to execute first
        # create intermediate components to use as inputs for clientside callback
        dcc.Store(id="peak-added", data=0),
        dcc.Store(id="peak-deleted", data=0)
    ]
)

# new peak accordion with all peak editing options
def peak_options(n_clicks):
    return dmc.Accordion(
        children=[
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(f"Peak {n_clicks}", id={"type": "peak-set-name", "index": n_clicks}),
                    dmc.AccordionPanel(
                        [
                            html.Div(
                                [
                                    dmc.ActionIcon(
                                        DashIconify(icon="material-symbols-light:cancel-outline", width=20),
                                        size="lg",
                                        color="red",
                                        variant="subtle",
                                        id={"type": "peak-delete", "index": n_clicks},
                                    )
                                ],
                                style={"display": "flex", "justifyContent": "flex-end"}
                            ),
                            html.Div(
                                [
                                    dbc.Input(value=f"Peak {n_clicks}", type="text", id={"type": "peak-edit-name", "index": n_clicks}),
                                    dbc.Button(DashIconify(icon="ph:pencil-thin"), disabled=True)
                                ],
                                className="accordian-options"
                            ),
                            html.Div(
                                [
                                    html.P("Peak Center:", style={"margin-top": 10}),
                                    dbc.Input(type="number", value=0, min=0, step=0.05, style={"width": 100, "margin-left": 20}, className="sidebar-input", id={"type": "peak-center", "index": n_clicks})
                                ],
                                className="accordian-options"
                            ),
                            html.Div(
                                [
                                    html.P("Peak Height:", style={"margin-top": 10}),
                                    dbc.Input(type="number", value=0, min=0, style={"width": 100, "margin-left": 20}, className="sidebar-input", id={"type": "peak-height", "index": n_clicks})
                                ],
                                className="accordian-options"
                            ),
                            html.Div(
                                [
                                    html.P("Peak Width:", style={"margin-top": 10}),
                                    dbc.Input(type="number", value=0.01, min=0.01, step=0.01, style={"width": 100, "margin-left": 20}, className="sidebar-input", id={"type": "peak-width", "index": n_clicks})
                                ],
                                className="accordian-options"
                            ),
                            html.Div(
                                [
                                    html.P("Skew Factor:", style={"margin-top": 10}),
                                    dbc.Input(type="number", value=0, step=0.1, min=-0.3, max=0.3, style={"width": 100, "margin-left": 20}, className="sidebar-input", id={"type": "peak-skew", "index": n_clicks})
                                ],
                                className="accordian-options"
                            ),
                        ],
                    ),
                ],
                value="peak-accordian",
            ),
        ],
    )

# Add / Delete another peak accordian with all peak options
@callback(
    Output("add-peak-container", "children"),
    Output("peak-added", "data"),
    Output("peak-deleted", "data"),
    Input("add-peak", "n_clicks"),
    Input({"type": "peak-delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def display_dropdowns(add_peak, del_peak):
    is_added = add_peak
    is_deleted = no_update
    patched_children = Patch()
    if ctx.triggered_id != "add-peak":
        is_deleted = True
        is_added = no_update
        values_to_remove = []
        for i, val in enumerate(del_peak):
            if val:
                # add idx backwards to preserve deletion idx
                values_to_remove.insert(0, i)
        for v in values_to_remove:
            del patched_children[v]
    else:
        peak = peak_options(add_peak)
        patched_children.append(peak)
    return patched_children, is_added, is_deleted

# Rename peak
@callback(
    Output({'type': 'peak-set-name', 'index': MATCH}, "children"),
    Input({'type': 'peak-edit-name', 'index': MATCH}, "value"),
    prevent_initial_call=True
)
def set_peak_name(name):
    return name
