from dash import Input, Output, State, clientside_callback, ClientsideFunction
import dash_ag_grid as dag
import dash_mantine_components as dmc

results_panel = dmc.TabsPanel(
    dag.AgGrid(
        id="results-table",
        columnDefs=[
            {
                "field": "RT",
                "width": 140,
                "sort": "asc",
            },
            {
                "field": "Name",
                "width": 140,
            },
            {
                "field": "Height",
                "width": 140,
            },
            {
                "field": "Area",
                "width": 140,
            },
            {
                "field": "Concentration",
                "width": 140,
            },
            {
                "field": "Units",
                "width": 140,
                "editable": True,
                "sortable": False,
                "cellRenderer": "editUnit",
            },
        ],
        dashGridOptions={
            "animateRows": True,
            },
        style={"width": None, "height": 500},
        className="ag-theme-balham-dark"
    ),
    value="results"
)

clientside_callback(
    ClientsideFunction(
        namespace="results",
        function_name='updateTable'
    ),
    Output("results-table", "rowData"),
    Input("integration-intermediate", "data"),
    Input("calibration-intermediate", "data"),
    Input("x-y-data", "data"),
    State("results-table", "columnDefs"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="results",
        function_name='updateUnits'
    ),
    Output("table-updates", "data", allow_duplicate=True),
    Input("results-table", "cellValueChanged"),
    State("x-y-data", "data"),
    prevent_initial_call=True
)
