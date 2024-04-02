import dash_mantine_components as dmc
from dash_extensions.enrich import html

from kmviz.ui.layouts.index import make_index_layout, make_index_layout_callbacks, kindex
from kmviz.ui.layouts.table import make_table_layout, make_table_layout_callbacks, ktable
from kmviz.ui.layouts.map import make_map_layout, make_map_layout_callbacks, kmap
from kmviz.ui.layouts.sequence import make_sequence_layout, make_sequence_layout_callbacks, kseq
from kmviz.ui.layouts.plot import make_plot_layout, make_plot_layout_callbacks, kplot
from kmviz.ui.layouts.help import make_help_layout

def make_tabs():
    tabs = html.Div([
        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab("Index", value="index", id=kindex.sid("panel")),
                dmc.Tab("Table", value="table", disabled=True, id=ktable.sid("panel")),
                dmc.Tab("Map", value="map", disabled=True, id=kmap.sid("panel")),
                dmc.Tab("Plot", value="plot", disabled=True, id=kplot.sid("panel")),
                dmc.Tab("Sequence", value="sequence", disabled=True, id=kseq.sid("panel")),
                dmc.Tab("Help", value="help"),
            ]),

            dmc.TabsPanel(make_table_layout(), value="table"),
            dmc.TabsPanel(make_map_layout(), value="map"),
            dmc.TabsPanel(make_index_layout(), value="index"),
            dmc.TabsPanel(make_sequence_layout(), value="sequence"),
            dmc.TabsPanel(make_plot_layout(), value="plot"),
            dmc.TabsPanel(make_help_layout(), value="help"),
        ], value="index", id="tab-select"),
    ])

    make_table_layout_callbacks()
    make_index_layout_callbacks()
    make_map_layout_callbacks()
    make_sequence_layout_callbacks()
    make_plot_layout_callbacks()

    return tabs

