from dash_extensions.enrich import html, Input, Output, State, callback, no_update, dcc
import dash
import dash_mantine_components as dmc
from kmviz.ui.layouts.sidebar import Sidebar
from kmviz.ui.layouts.tabs import Tabs
from kmviz.ui.layouts import Global

from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import dmc_new
import kmviz.core.config as kconf
from kmviz.core.log import kmv_info

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
    kmv_info(f"Load session {str(data)}")
    if n_i == 1:
            return 500, data
    return no_update, no_update

def make_dashboard(session_id=None):
    G = Global(kconf.st)
    S = Sidebar(kconf.st)
    T = Tabs(kconf.st)

    if dmc_new:
        layout = dmc.AppShell(
            id="kmviz-shell",
            children=[
                G.layout(),
                dmc.AppShellNavbar(S.layout(), className="kmviz-sidebar"),
                dmc.AppShellMain(T.layout())
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

        has_session = True
        if session_id and not kconf.st.cache.has(session_id):
            has_session = False

        layout = html.Div([
            G.layout(),
            dmc.Grid([
                dmc.Col(S.layout(), id=kid.kmviz["side-layout"], span="content", className="kmviz-sidebar-layout"),
                dmc.Col(T.layout(), id=kid.kmviz["main-layout"], span="auto", className="kmviz-main-layout", style = style),
                dcc.Interval(id="kmviz-session-interval", max_intervals=1, n_intervals=0, interval=100),
                dcc.Store(id="kmviz-session-store-page", data=str(session_id)),
                dmc.Modal(
                    title=dmc.Text(str(session_id), color="red"),
                    id="kmviz-load-modal",
                    zIndex=10000,
                    children=[dmc.Text(f"'{str(session_id)}' not found. Maybe your query is still running?")],
                    opened=not has_session,
                    withCloseButton=False,
                    shadow=True
                ),
            ])
        ])

    return layout

dash.register_page(__name__, path_template=kconf.st.instance_plugin[0] + "/<session_id>", path=kconf.st.instance_plugin[0], name="dashboard", title="dashboard")

layout = make_dashboard
