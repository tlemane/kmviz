import dash_mantine_components as dmc
from dash_extensions.enrich import html, callback

from kmviz import __version__ as kmviz_version

from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.select import make_select_provider, make_select_provider_callbacks
from kmviz.ui.components.input import make_input, make_input_callbacks
from kmviz.ui.components.option import make_config, make_config_callbacks
from kmviz.ui.components.submit import make_submit, make_submit_callbacks

klf = kf.child("layout")

def make_sidebar_layout():
    res = html.Div([
        dmc.Center([
            html.H1(f"kmviz v{kmviz_version}"),
        ]),
        dmc.Space(h=5),
        make_select_provider(),
        dmc.Space(h=20),
        make_input(),
        dmc.Space(h=20),
        make_config(),
        dmc.Space(h=20),
        make_submit()
    ], className="sidebar", id=klf.sid("sidebar-div"))

    return res

def make_sidebar_layout_callbacks():

    make_select_provider_callbacks()
    make_input_callbacks()
    make_config_callbacks()
    make_submit_callbacks()
