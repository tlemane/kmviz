import dash_mantine_components as dmc
from dash_extensions.enrich import html, callback, Input, Output, State, Serverside, no_update, clientside_callback
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import khide
from kmviz.ui.components.helpers import load_file_as_df
from kmviz.ui.layouts.input import SideInputLayout, SideDBLayout
from kmviz.ui.layouts.config import ConfigLayout
from kmviz.ui.layouts.submit import SubmitLayout
from kmviz.ui.layouts.notif import NotifLayout

from kmviz.ui.id_factory import kid
from kmviz.ui.utils import icons
from kmviz.core.io import KmVizIOError
from kmviz.core.config import state

import kmviz

class Sidebar:
    def __init__(self, st: state):
        self.st = st
        self.mode = st.mode

        if self.mode == "db":
            self.sinput = SideInputLayout(self.st)
            self.sdb = SideDBLayout(self.st)
            self.sconfig = ConfigLayout(self.st)
            self.ssubmit = SubmitLayout(self.st)
            self.snotif = NotifLayout(self.st)

    def _make_database_layout(self) -> html.Div:
        layout = cf.div(
            kid.kmviz["side-div"],
            dmc.Center(cf.h1(f"kmviz {kmviz.__version_str__}")),
            self.sdb.layout(),
            self.sinput.layout(),
            self.snotif.layout(),
            self.sconfig.layout(),
            self.ssubmit.layout(),
        )

        return layout

    def _make_plot_mode_layout(self) -> html.Div:
        return cf.div(
            kid.pom["div"],
            dmc.Center(cf.h4("Plot Mode")),
            cf.divider(size="sm", color="gray", label="CONFIG", labelPosition="center"),
            cf.group(
                kid.pom["grp-1"],
                cf.text(kid.pom["index"], label="Index", required=True,  classNames={"root": "kmviz-dmc-text-input-root"}),
                cf.text(kid.pom["sep"], label="Separator",  classNames={"root": "kmviz-dmc-text-input-root"})
            ),
            cf.group(
                kid.pom["grp-2"],
                cf.text(kid.pom["latitude"], label="Latitude", classNames={"root": "kmviz-dmc-text-input-root"}),
                cf.text(kid.pom["longitude"], label="Longitude", classNames={"root": "kmviz-dmc-text-input-root"})
            ),
            dmc.Space(h=10),
            dmc.Center(
                cf.upload(
                    kid.pom["upload"],
                    cf.button(kid.pom["load-button"], "Load (csv,tsv,xlsx)", disabled=True, leftSection=icons("file")),
                ),
            ),
            cf.div(kid.pom["error"]),
        )

    def _plot_mode_callbacks(self) -> None:

        @callback(
            Input(kid.pom["index"], "value"),
            Output(kid.pom["load-button"], "disabled"),
            prevent_initial_call=True
        )
        def enable_button(value):
            if value:
                return False
            return True

        @callback(
            Input(kid.pom["upload"], "filename"),
            Input(kid.pom["upload"], "contents"),
            State(kid.pom["index"], "value"),
            State(kid.pom["sep"], "value"),
            State(kid.pom["latitude"], "value"),
            State(kid.pom["longitude"], "value"),
            Output(kid.pom["store"], "data"),
            Output(kid.pom["error"], "children"),
            Output(kid.kmviz["side-layout"], "style"),
            Output(kid.kmviz["main-layout"], "style"),
            prevent_initial_call=True
        )
        def upload_df_file(filename, contents, index, sep, lat, lon):
            try:
                df = load_file_as_df(filename, contents, sep)
                df.rename(columns={index: "ID"}, inplace=True)

                res = dict(df=df, geodata=None)

                if lat and lon:
                    if lat in list(df) and lon in list(df):
                        res["geodata"] = { "latitude": lat, "longitude": lon}
                    else:
                        KmVizIOError(f"'{lat}' or '{lon}' not found in dataframe")

                return Serverside(res), [], khide, {"padding-left": "10px"}

            except KmVizIOError as e:
                no_update, dmc.Text(str(e), color="red", weight=500), no_update, no_update

    def _database_callbacks(self) -> None:
        self.sinput.callbacks()
        self.sdb.callbacks()
        self.sconfig.callbacks()
        self.ssubmit.callbacks()
        self.snotif.callbacks()

    def layout(self) -> html.Div:
        if self.mode == "plot":
            return self._make_plot_mode_layout()
        elif self.mode == "db":
            return self._make_database_layout()

    def callbacks(self) -> None:
        if self.mode == "plot":
            self._plot_mode_callbacks()
        elif self.mode == "db":
            self._database_callbacks()
