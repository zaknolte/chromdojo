import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, dcc

from components.sidebar import sidebar
from components.graph import graph
from components.data_tabs import data_tab


app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
)

server = app.server

# mantine provider required root wrapper for using mantine components ANYWHERE in app
app.layout = dmc.MantineProvider(
    html.Div(
        [
            sidebar,
            html.Div(
                [
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Welcome to Chrom-Dojo!")),
                            dbc.ModalBody(
                                """To begin building your own chromatograms, hover over the options sidebar on the left to display peak options.\n
                                \nAdd as many peaks as you want with the '+ Add Peak" button and begin customizing peak shape, noise, and baseline.\n
                                \nIf you want to test quantitative data, you can adjust integration parameters as well as create custom calibration curves in the table below!
                                """
                            ),
                            dbc.ModalFooter("Have fun!")
                        ],
                        id="modal",
                        is_open=True,
                    ),
                    graph,
                    data_tab,
                    dcc.Store(id="x-y-data", data=None), # hold major updates to peak data
                    dcc.Store(id="integration-intermediate", data=None),
                    dcc.Store(id="integration-data", data=None),
                    dcc.Store(id="annotation-data", data=None),
                    dcc.Store(id="calibration-intermediate", data=None),
                    dcc.Store(id="table-updates", data=None), # trigger minor updates from calibration / results updates
                ],
                className="content"
            )
        ],
    )
)

if __name__ == "__main__":
    app.run_server(debug=False)
