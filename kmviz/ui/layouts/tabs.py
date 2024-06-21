import dash_mantine_components as dmc
from dash_extensions.enrich import html

from kmviz.ui.layouts.index import make_index_layout, make_index_layout_callbacks, kindex
from kmviz.ui.layouts.table import make_table_layout, make_table_layout_callbacks, ktable
from kmviz.ui.layouts.map import make_map_layout, make_map_layout_callbacks, kmap
from kmviz.ui.layouts.sequence import make_sequence_layout, make_sequence_layout_callbacks, kseq
from kmviz.ui.layouts.plot import make_plot_layout, make_plot_layout_callbacks, kplot
from kmviz.ui.layouts.help import make_help_layout
from dash_iconify import DashIconify
from kmviz.ui import state
from kmviz.core.log import kmv_info

def _make_plugin_tab(plugin, name, icon):
    hide = {"display":"none"} if state.kmstate.plot_only else {}

    return dmc.Tab(
        name,
        value=f"{plugin}-{name}-value",
        id=f"kmviz-plugin-{plugin}-{name}-id",
        style=hide,
        icon=DashIconify(icon=icon) if icon else None
    )

def _make_plugin_panel(plugin, name, panel):
    return dmc.TabsPanel(
        panel, value=f"{plugin}-{name}-value"
    )

def make_tabs():
    hide = {"display":"none"} if state.kmstate.plot_only else {}

    pTabs = []
    pPanels = []

    for name, plugin in state.kmstate.plugins.items():
        layouts = plugin.layouts()
        if layouts:
            for tab_name, panel, icon in layouts:
                kmv_info(f"Load layout '{tab_name}' from plugin '{name}'")
                pTabs.append(_make_plugin_tab(name, tab_name, icon))
                pPanels.append(_make_plugin_panel(name, tab_name, panel))

    tabs = html.Div([
        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab(
                    "Index",
                    value="index",
                    id=kindex.sid("panel"),
                    icon=DashIconify(icon="iconoir:db"),
                    style = hide),
                dmc.Tab(
                    "Table",
                    value="table",
                    disabled=True,
                    id=ktable.sid("panel"),
                    icon=DashIconify(icon="material-symbols:table")),
                dmc.Tab(
                    "Map",
                    value="map",
                    disabled=True,
                    id=kmap.sid("panel"),
                    icon=DashIconify(icon="fluent-mdl2:world"),),
                dmc.Tab(
                    "Plot",
                    value="plot",
                    disabled=True,
                    id=kplot.sid("panel"),
                    icon=DashIconify(icon="carbon:qq-plot"),),
                dmc.Tab(
                    "Sequence",
                    value="sequence",
                    disabled=True,
                    id=kseq.sid("panel"),
                    icon=DashIconify(icon="mdi:dna"),
                    style = hide),
                *pTabs,
                dmc.Tab(
                    "Help",
                    value="help",
                    icon=DashIconify(icon="material-symbols:help-outline")),
            ], className="kmviz-tab-header"),

            html.Div([

            dmc.TabsPanel(
                make_table_layout(), value="table"),
            dmc.TabsPanel(
                make_map_layout(), value="map"),
            dmc.TabsPanel(
                make_index_layout(), value="index"),
            dmc.TabsPanel(
                make_sequence_layout(), value="sequence"),
            dmc.TabsPanel(
                make_plot_layout(), value="plot"),
            *pPanels,
            dmc.TabsPanel(
                make_help_layout(), value="help"),
            ], className="kmviz-tabs")
        ], value="index" if not state.kmstate.plot_only else None, id="tab-select"),
    ])

    make_table_layout_callbacks()
    make_index_layout_callbacks()
    make_map_layout_callbacks()
    make_sequence_layout_callbacks()
    make_plot_layout_callbacks()

    return tabs

