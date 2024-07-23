from dash_extensions.enrich import html
import dash
import dash_mantine_components as dmc
from kmviz.ui.layouts.sidebar import Sidebar
from kmviz.ui.layouts.tabs import Tabs
from kmviz.ui.layouts import Global

from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import dmc_new
import kmviz.core.config as kconf

def make_dashboard():

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
            ])
        ])

    glob.callbacks()
    sidebar.callbacks()
    tabs.callbacks()

    return layout

dash.register_page(__name__, path=kconf.st.instance_plugin[0], name="dashboard", title="dashboard")

layout = make_dashboard()
