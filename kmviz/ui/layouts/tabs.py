from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.utils import icons
from kmviz.ui.components.factory import khide, kshow, km_color
from kmviz.ui.id_factory import kid
from kmviz.core.config import state
from kmviz.core.query import QueryResponseGeo
from dash_iconify import DashIconify
from dash_extensions.enrich import dcc, callback, Input, Output, State
from kmviz.ui.layouts.index import Index
from kmviz.ui.layouts.table import TableLayout
from kmviz.ui.layouts.sequence import SequenceLayout
from kmviz.ui.layouts.figure.plot import PlotLayout
from kmviz.ui.layouts.figure.map import MapLayout
from kmviz.ui.layouts.help import HelpLayout
from kmviz.ui.layouts.session import SessionLayout
from dash.exceptions import PreventUpdate
from flask import jsonify
import dash_mantine_components as dmc
import orjson

class Tabs:
    def __init__(self, st: state):
        self._tabs = []
        self._panels = []
        self.st = st

        self.dtab = None

        if self.st.mode == "session" or self.st.mode == "plot":
            self.dtab = "table"

        self.plugin_show = khide if self.st.mode in ("plot", "session") else {}

        self._index = Index(self.st)
        self._table = TableLayout(self.st)
        self._sequence = SequenceLayout(self.st)
        self._plot = PlotLayout(self.st, kid.plot, kid.plot["figure"], kid.table("grid"))
        self._map = MapLayout(self.st, kid.map, kid.map["figure"], kid.table("grid"))
        self._session = SessionLayout(self.st, kid.session)
        self._help = HelpLayout(self.st, kid.help)

        self._disabled = False if self.st.mode in ("plot", "session") else True

    def _plugin_layout(self):
        for name, plugin in self.st.conf.plugins.items():
            layouts = plugin.layouts()
            if layouts:
                for tab_name, panel, icon in layouts:
                    self._tabs.append(
                        cf.tabs_tab(
                            kid.plugin[f"{name}-{tab_name}-tab"],
                            tab_name,
                            value=f"{name}-{tab_name}-tab",
                            leftSection=DashIconify(icon=icon) if icon else None,
                            style=self.plugin_show
                        )
                    )
                    self._panels.append(
                        cf.tabs_panel(
                            kid.plugin[f"{name}-{tab_name}-panel"],
                            panel,
                            value=f"{name}-{tab_name}-tab",
                        )
                    )

    def _index_layout(self):

        self._tabs.append(
            cf.tabs_tab(
                kid.tabs["index"],
                "Index",
                value="index",
                leftSection=DashIconify(icon="iconoir:db"),
                disabled=self._disabled,
                style = khide.copy() if not self.st.ui.with_index_tab else {}
            )
        )
        self._panels.append(
            cf.tabs_panel(
                kid.tabs["index-panel"],
                self._index.layout(),
                value="index",
            )
        )

    def _index_callbacks(self) -> None:
        self._index.callbacks()

    def _table_layout(self):
        self._tabs.append(
            cf.tabs_tab(
                kid.tabs["table"],
                "Table",
                value="table",
                leftSection=DashIconify(icon="material-symbols:table"),
                disabled=self._disabled
            )
        )
        self._panels.append(
            cf.tabs_panel(
                kid.tabs["table-panel"],
                self._table.layout(),
                value="table"
            )
        )

    def _table_callbacks(self) -> None:
        self._table.callbacks()

    def _map_layout(self):
        self._tabs.append(
            cf.tabs_tab(
                kid.tabs["map"],
                "Map",
                value="map",
                leftSection=DashIconify(icon="fluent-mdl2:world"),
                disabled=self._disabled,
                style = khide.copy() if not self.st.ui.with_map_tab else {}
            )
        )
        self._panels.append(
            cf.tabs_panel(
                kid.tabs["map-panel"],
                self._map.layout(),
                value="map"
            )
        )

    def _map_callbacks(self) -> None:
        self._map.callbacks()

    def _plot_layout(self):
        self._tabs.append(
            cf.tabs_tab(
                kid.tabs["plot"],
                "Plot",
                value="plot",
                leftSection=DashIconify(icon="carbon:qq-plot"),
                disabled=self._disabled,
                style = khide.copy() if not self.st.ui.with_plot_tab else {}
            )
        )
        self._panels.append(
            cf.tabs_panel(
                kid.tabs["plot-panel"],
                self._plot.layout(),
                value="plot"
            )
        )

    def _plot_callbacks(self) -> None:
        self._plot.callbacks()

    def _sequence_layout(self):
        self._tabs.append(
            cf.tabs_tab(
                kid.tabs["sequence"],
                "Sequence",
                value="sequence",
                leftSection=DashIconify(icon="mdi:dna"),
                disabled=self._disabled,
                style = khide.copy() if not self.st.ui.with_sequence_tab else {}
            )
        )
        self._panels.append(
            cf.tabs_panel(
                kid.tabs["sequence-panel"],
                self._sequence.layout(),
                value="sequence"
            )
        )

    def _sequence_callbacks(self) -> None:
        self._sequence.callbacks()

    def _help_layout(self):
        self._tabs.append(
            cf.tabs_tab(
                kid.tabs["help"],
                "Help",
                value="help",
                leftSection=DashIconify(icon="material-symbols:help-outline"),
                style = khide.copy() if not self.st.ui.with_help_tab else {}
            )
        )
        self._panels.append(
            cf.tabs_panel(
                kid.tabs["help-panel"],
                self._help.layout(),
                value="help"
            )
        )

    def _help_callbacks(self) -> None:
        self._help.callbacks()

    def _corner_layout(self):
        style = kshow if self.st.mode != "plot" else khide

        group_content = [
            dcc.Download(id=kid.kmviz["download"]),
            cf.switch( kid.kmviz("auto"), onLabel=icons("autoff", width=20), offLabel=icons("auton", width=20), checked=True),
            dmc.Space(w=3, style=style),
            cf.action( kid.kmviz["download-button"], DashIconify(icon="bi:filetype-json", width=25), variant="filled", color = km_color, style=style),
            dmc.Space(w=5, style=style),
            cf.select( kid.kmviz("database"), data=[], placeholder="Database", size="xs", style=style),
            cf.select( kid.kmviz("query"), data=[], placeholder="Query", size="xs", style=style),
        ]
        self._tabs.append(cf.group(
            kid.kmviz["corner-grp"],
            *group_content,
            gap=4
        ))

    def _corner_callbacks(self) -> None:
        @callback(
            Input(kid.kmviz["download-button"], "n_clicks"),
            State(kid.store["results"], "data"),
            State(kid.store["session-id"], "data"),
            Output(kid.kmviz["download"], "data")
        )
        def download_all(n_clicks, data, session):
            if n_clicks and len(data) and self.st.engine.list():
                for qname, res in data.items():
                    for name in res:
                        R = QueryResponseGeo(
                            res[name]._query,
                            res[name]._response,
                            orjson.loads(res[name].df.to_json()),
                            self.st.engine.get(name).db.geodata
                        )
                        res[name] = R

                return dict(content=orjson.dumps(jsonify({session: data}).json).decode(), filename=f"session.json")
            raise PreventUpdate

    def _session_layout(self):
        self._tabs.append(
            self._session.layout()
        )

    def _session_callbacks(self):
        self._session.callbacks()

    def layout(self):
        if self.st.mode == "db":
            self._index_layout()

        self._table_layout()
        self._map_layout()
        self._plot_layout()

        if self.st.mode != "plot":
            self._sequence_layout()

        self._plugin_layout()
        self._help_layout()


        if self.st.mode == "session":
            self._session_layout()

        self._corner_layout()

        return cf.tabs(
            kid.tabs["tabs"],
            cf.tabs_list(
                kid.tabs["header"],
                *self._tabs
            ),
            *self._panels,
            value=self.dtab,
            allowTabDeactivation=True,
        )

    def callbacks(self):
        if self.st.ui.with_index_tab:
            self._index_callbacks()
        self._table_callbacks()

        if self.st.ui.with_map_tab:
            self._map_callbacks()
        if self.st.ui.with_plot_tab:
            self._plot_callbacks()
        if self.st.ui.with_sequence_tab:
            self._sequence_callbacks()

        self._corner_callbacks()

        if self.st.mode == "session":
            self._session_callbacks()
