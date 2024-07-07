from dash import html
import dash_mantine_components as dmc

from components.results_panel import results_panel
from components.calibration_panel import calibration_panel

data_tab = html.Div(
    [
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.TabsTab("Results", value="results"),
                        dmc.TabsTab("Calibration Curves", value="curves"),
                    ],
                    justify="center"
                ),
                results_panel,
                calibration_panel
            ],
            value="results",
            color="red",
            style={"width": "60%"}
        ),
    ],
    style={"display": "flex", "justifyContent": "center"}
)
