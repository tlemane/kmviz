from dash_extensions.enrich import html, dcc, Input, Output, State, no_update, callback
import dash
import dash_mantine_components as dmc
from kmviz.ui.layouts.sidebar import Sidebar
from kmviz.ui.layouts.tabs import Tabs
from kmviz.ui.layouts import Global

from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import dmc_new
import kmviz.core.config as kconf

Global(kconf.st).callbacks()
Sidebar(kconf.st).callbacks()
Tabs(kconf.st).callbacks()

@callback(
    Input("kmviz-session-interval", "n_intervals"),
    State(kid.input["session-button"], "n_clicks"),
    State("kmviz-session-store-page", "data"),
    Output(kid.input["session-button"], "n_clicks"),
    Output(kid.input("session"), "value"),
)
def load_session_page(n_i, n_c, data):
    print(n_i, data)
    if n_i == 1:
        return 500, data
    return no_update, no_update

def make_dashboard(session_id=None):
    glob = Global(kconf.st)
    sidebar = Sidebar(kconf.st)
    tabs = Tabs(kconf.st)

    if dmc_new:
        layout = dmc.AppShell(
            id="kmviz-shell",
            children=[
                glob.layout(),
                dmc.AppShellNavbar(sidebar.layout(), className="kmviz-sidebar"),
                dmc.AppShellMain(tabs.layout())
            ],
            navbar={
                "width": 250,
                "breakpoint": "lg",
                "collapsed": {"mobile": True},
            },
            transitionDuration="50",
            className="kmviz-main"
        )
    else:
        style={}
        if kconf.st.mode == "session":
            style = {"padding-left": "10px"}

        layout = html.Div([
            glob.layout(),
            dmc.Grid([
                dmc.Col(sidebar.layout(), id=kid.kmviz["side-layout"], span="content", className="kmviz-sidebar-layout"),
                dmc.Col(tabs.layout(), id=kid.kmviz["main-layout"], span="auto", className="kmviz-main-layout", style = style),
                dcc.Interval(id="kmviz-session-interval", max_intervals=1, n_intervals=0, interval=100),
                dcc.Store(id="kmviz-session-store-page", data=str(session_id))
            ])
        ])


    return layout

dash.register_page(__name__, path_template=kconf.st.instance_plugin[0] + "/<session_id>", path=kconf.st.instance_plugin[0], name="dashboard", title="dashboard")

layout = make_dashboard
