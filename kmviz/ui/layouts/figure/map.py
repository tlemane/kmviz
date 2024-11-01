from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color, khide, kshow
from dash_extensions.enrich import html, dcc, callback, Input, Output, State, ctx, no_update
import plotly.graph_objects as go
import plotly.io as pio
from kmviz.ui.utils import icons, make_select_data
from dash.exceptions import PreventUpdate

from kmviz.core.log import kmv_debug
import plotly.express as px
from dash import Patch
from kmviz.ui.id_factory import kid
from kmviz.ui.layouts.figure.plotly import select_cscale
from kmviz.ui.layouts.figure.title import TitleLayout
from kmviz.ui.layouts.figure.axe import AxesLayout
from kmviz.ui.layouts.figure.legend import LegendLayout
from kmviz.ui.layouts.figure.shape import ShapeLayout
from kmviz.ui.layouts.figure.download_graph import DownloadGraphLayout
from kmviz.ui.layouts.filter import FilterLayout
from kmviz.ui.layouts.figure import apply_presets, apply_legend_and_title_presets
from kmviz.ui.layouts.figure.color import ColorLegendLayout
from kmviz.ui.presets import set_preset_values

from kmviz.ui.components.helpers import from_json
from kmviz.core.config import state

from dash_iconify import DashIconify

import pandas as pd
from pandas.api.types import is_numeric_dtype

import dash_mantine_components as dmc

class MapTraceLayout:

    def __init__(self, st: state, factory, figure_id, figure_data, preset):
        self.st = st
        self.f = factory
        self.fid = figure_id
        self.fdata = figure_data
        self.preset = preset

    def _data_panel(self):
        return cf.tabs_panel(
            self.f["data-panel"],
            cf.group(
                self.f["data-grp-1"],
                cf.select(self.f("color"), [], label="Color", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("size"), [], label="Size", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("text"), [], label="Text", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("symbol"), [], label="Symbol", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
            ),
            value="data"
        )

    def _anim_panel(self):
        return cf.tabs_panel(
            self.f["anim-panel"],
            cf.group(
                self.f["anim-grp-1"],
                cf.select(self.f("animation_frame"), [], label="Frame", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("animation_group"), [], label="Group", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
            ),
            value="anim"
        )

    def _style_panel(self):
        return cf.tabs_panel(
            self.f["style-panel"],
            [
                cf.group(
                    self.f["style-grp-1"],
                    cf.select(self.f("template"), list(pio.templates), label="Theme", clearable=True, searchable=True, size="xs", className="kmviz-figure-select", leftSection=icons("style", width=20)),
                    cf.select(self.f("projection"), [ 'equirectangular', 'mercator', 'orthographic', 'natural earth', 'kavrayskiy7', 'miller', 'robinson', 'eckert4', 'azimuthal equal area', 'azimuthal equidistant', 'conic equal area', 'conic conformal', 'conic equidistant', 'gnomonic', 'stereographic', 'mollweide', 'hammer', 'transverse mercator', 'albers usa', 'winkel tripel', 'aitoff', 'sinusoidal' ], label="Projection", value="equirectangular", clearable=True, searchable=True, className="kmviz-figure-select", size="xs", icon=icons("map") ),
                    cf.sseqscale(self.f("color_seq_continuous_scale"), label="Color sequential scale", clearable=True, searchable=True, size="xs", className="kmviz-figure-select"),
                    cf.sdivscale(self.f("color_div_continuous_scale"), label="Color diverging scale", clearable=True, searchable=True, size="xs", className="kmviz-figure-select"),
                    cf.scycscale(self.f("color_cyc_continuous_scale"), label="Color cyclical scale", clearable=True, searchable=True, size="xs", className="kmviz-figure-select"),
                    cf.number(self.f("color_continuous_midpoint"), label="Color midpoint", min=None, max=None, step=None, value=None, leftSection=icons("floating"), decimalScale=2, size="xs"),
                    cf.number(self.f("opacity"), label="Opacity", min=0.0, max=1.0, step=0.01, value=0.7, leftSection=icons("floating"), decimalScale=2, size="xs"),
                    cf.number(self.f("size_max"), label="Max size", min=0, max=50, step=1, value=15, leftSection=icons("integer"), decimalScale=2, size="xs"),
                ),
                cf.group(
                    self.f["style-grp-2"],
                    cf.json(self.f("color_discrete_map"), placeholder='ex: {"v1": "blue", "v2": "red"}', label="Color map", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("symbol_map"), placeholder='ex: {"v1": "circle-open", "v2": "square-open"}', label="Symbol map", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("color_discrete_sequence"), placeholder='ex: {"seq": ["red", "blue"] }', label="Color sequence", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("symbol_sequence"), placeholder='ex: {"seq": ["circle-open", "square-open"] }', label="Symbol sequence", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    grow=True,
                ),
            ],
            value="style"
        )

    def layout(self):
        return cf.tabs(
            self.f["tabs"],
            cf.tabs_list(
                self.f["tabslist"],
                cf.tabs_tab(self.f["data-tab"], "Data", value="data"),
                cf.tabs_tab(self.f["anim-tab"], "Animation", value="anim"),
                cf.tabs_tab(self.f["style-tab"], "Style", value="style"),
            ),
            self._data_panel(),
            self._anim_panel(),
            self._style_panel(),

            value="data"
        )

    def callbacks(self):

        @callback(
            Input(self.fdata, "virtualRowData"),
            Output(self.f("color"), "data"),
            Output(self.f("text"), "data"),
            Output(self.f("symbol"), "data"),
            Output(self.f("animation_frame"), "data"),
            Output(self.f("animation_group"), "data"),
            Output(self.f("size"), "data"),
            prevent_initial_call=True
        )
        def update_data(data):
            if not data:
                raise PreventUpdate

            df = pd.DataFrame.from_dict(data)
            cols = make_select_data(list(df))
            cols_size = []
            for c in list(df):
                if is_numeric_dtype(df[c]):
                    if all(x >= 0 for x in df[c]):
                        cols_size.append(c)

            return (cols,) * 5 + (cols_size,)


        @callback(
            Output(self.fid, "figure"),
            Input(self.fdata, "virtualRowData"),
            Input(self.f("template"), "value"),
            Input(self.f("color"), "value"),
            Input(self.f("size"), "value"),
            Input(self.f("text"), "value"),
            Input(self.f("symbol"), "value"),
            Input(self.f("animation_frame"), "value"),
            Input(self.f("animation_group"), "value"),
            Input(self.f("projection"), "value"),
            Input(self.f("color_seq_continuous_scale"), "value"),
            Input(self.f("color_div_continuous_scale"), "value"),
            Input(self.f("color_cyc_continuous_scale"), "value"),
            Input(self.f("color_continuous_midpoint"), "value"),
            Input(self.f("symbol_map"), "value"),
            Input(self.f("symbol_sequence"), "value"),
            Input(self.f("color_discrete_map"), "value"),
            Input(self.f("color_discrete_sequence"), "value"),
            Input(self.f("opacity"), "value"),
            Input(self.f("size_max"), "value"),
            State(kid.store["session-id"], "data"),
            State(kid.kmviz("database"), "value"),
            State(kid.pom["store"], "data"),
            Input(self.preset, "value"),
            prevent_initial_call=True
        )
        def make_plot(data, template, color, size, text, symbol, aframe, agroup,
                      projection, cscs, cdcs, cccs, ccm, smap, sseq, cdm, cds, opacity,
                      size_max, session, database, pom, preset):

            kmv_debug(f"{session}: 'update_map' triggered by '{ctx.triggered_id}'")

            if not data:
                raise PreventUpdate

            if pom and "geodata" not in pom and not "session" in pom:
                return None

            df = pd.DataFrame.from_dict(data)

            scale = select_cscale([cscs, cdcs, cccs])

            if "geodata" in pom:
                geo = pom["geodata"]
            elif "session" in pom:
                geo = pom["session"][database]
            else:
                geo = self.st.engine.get(database).db.geodata

            if not geo:
                return None

            params = {
                "lat": geo["latitude"],
                "lon": geo["longitude"],
                "size": size,
                "color": color,
                "text": text,
                "symbol": symbol,
                "animation_frame": aframe,
                "animation_group": agroup,
                "color_continuous_midpoint": ccm,
                "color_continuous_scale": scale,
                "symbol_map": from_json(smap),
                "symbol_sequence": from_json(sseq, "seq"),
                "color_discrete_map": from_json(cdm),
                "color_discrete_sequence": from_json(cds, "seq"),
                "opacity": opacity,
                "size_max": size_max,
                "template": template,
                "projection": projection,
            }

            if self.st.conf.preset == "fixed":
                if preset and preset in self.st.engine.get(database).presets.map:
                    presets = self.st.engine.get(database).presets.map

                    params = apply_presets(presets[preset].model_dump(exclude=["title", "legend"]), params, self.st.engine.get(database).presets.priority)
                    fig = px.scatter_geo(df, hover_name="ID", **params)
                    apply_legend_and_title_presets(fig, presets[preset])
                    return fig

            return px.scatter_geo(df, hover_name="ID", **params)

        @callback(
            Input(self.fid, "selectedData"),
            Output(self.fdata, "filterModel"),
            prevent_initial_call=True
        )
        def on_selected(sdata):
            trigger = ctx.triggered_id

            if trigger == self.fid:
                conditions = []

                if sdata is None:
                    return {}

                for data in sdata["points"]:
                    conditions.append(
                        {"filter": data["hovertext"], "filterType":"text", "type":"equals"}
                    )

                p = Patch()
                p["ID"] = { "filterType": "text", "operator":"OR", "conditions": conditions }
                return p

            raise PreventUpdate

        if self.st.mode != "plot" and self.st.ui.with_sequence_tab:
            @callback(
                Input(self.fid, "clickData"),
                Output(kid.sequence["sample"], "value"),
                Output(self.fdata, "filterModel"),
                Output(kid.tabs["tabs"], "value"),
                prevent_initial_call=True,
            )
            def on_click_data_map(value):
                sample = value["points"][0]["hovertext"]

                p = Patch()
                p["ID"] = {'filterType': 'text', 'type': 'equals', 'filter': sample}

                return sample, p, "sequence"

class MapLayout:
    def __init__(self, st: state, factory, figure_id, figure_data):
        self.st = st
        self.f = factory
        self.fid = figure_id
        self.fdata = figure_data

        self._trace = MapTraceLayout(self.st, self.f.new("trace"), self.fid, self.fdata, self.f["preset"])
        self._title = TitleLayout(self.f.new("title"), self.fid)
        self._axes = AxesLayout(self.f.new("axes"), self.fid)
        self._legend = LegendLayout(self.f.new("legend"), self.fid)
        self._clegend = ColorLegendLayout(self.f.new("clegend"), self.fid)
        self._shape = ShapeLayout(self.f.new("shape"), self.fid)
        self._dl = DownloadGraphLayout(self.f.new("download"), self.fid, "plot")
        self._filter = FilterLayout(self.f.new("filter"), self.fdata)

    def _blank(self) -> go.Figure:
        fig = go.Figure(go.Scattergeo())
        fig.update_layout(template = "seaborn")
        fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
        fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
        return fig

    def _make_graph(self) -> dcc.Graph:
        return dcc.Loading(id=self.f("loading"), type="default", delay_show=250, children=[
            dcc.Graph(
                id=self.fid,
                figure=self._blank(),
                responsive=True,
                mathjax=True,
                className="kmviz-dcc-plot-graph",
                config = {
                    "modeBarButtonsToAdd": [
                        "drawline", "drawopenpath", "drawclosedpath", "drawcircle", "drawrect", "eraseshape"
                    ]
                }
            )
        ])

    def _make_tabs(self):
        return cf.tabs(
            self.f["tabs"],
            cf.tabs_list(
                self.f["tabslist"],
                cf.tabs_tab(self.f["trace-tab"], "Trace", value="trace"),
                cf.tabs_tab(self.f["title-tab"], "Title", value="title"),
                cf.tabs_tab(self.f["axes-tab"], "Axes", value="axes"),
                cf.tabs_tab(self.f["legend-tab"], "Legend", value="legend"),
                cf.tabs_tab(self.f["clegend-tab"], "Colorbar", value="clegend"),
                cf.tabs_tab(self.f["shape-tab"], "Shape", value="shape"),
                self._dl.layout(),
                dmc.Space(w=10),
                self._filter.layout(),
                cf.select(self.f["preset"], [], placeholder="Preset", clearable=True, icon=icons("preset"), size="xs", className="kmviz-figure-select kmviz-preset-select", style=khide),
            ),
            cf.tabs_panel(self.f["trace-panel"], self._trace.layout(), value="trace"),
            cf.tabs_panel(self.f["title-panel"], self._title.layout(), value="title"),
            cf.tabs_panel(self.f["axes-panel"], self._axes.layout(), value="axes"),
            cf.tabs_panel(self.f["legend-panel"], self._legend.layout(), value="legend"),
            cf.tabs_panel(self.f["clegend-panel"], self._clegend.layout(), value="clegend"),
            cf.tabs_panel(self.f["shape-panel"], self._shape.layout(), value="shape"),
            value="trace"
        )

    def layout(self) -> html.Div:
        return cf.div(
            self.f["div"],
            self._make_graph(),
            self._make_tabs(),
        )

    def callbacks(self) -> None:
        self._trace.callbacks()
        self._title.callbacks()
        self._axes.callbacks()
        self._legend.callbacks()
        self._clegend.callbacks()
        self._shape.callbacks()
        self._dl.callbacks()
        self._filter.callbacks()

        @callback(
            Input(self.f["rmf"], "n_clicks"),
            Output(self.fdata, "filterModel"),
            prevent_initial_call=True
        )
        def rmf(n_clicks):
            if n_clicks:
                return {}
            raise PreventUpdate

        @callback(
            Input(kid.kmviz("database"), "value"),
            Output(self.f["preset"], "data"),
            Output(self.f["preset"], "style"),
            Output(self.f["preset"], "value"),
            prevent_initial_call=True
        )
        def update_presets(db):
            if db.startswith("__kmviz_df") or self.st.mode != "db":
                raise PreventUpdate

            presets = self.st.engine.get(db).presets

            if presets.map:
                return make_select_data(list(presets.map.keys())), kshow, presets.defaults.map
            else:
                return [], khide, None

        if self.st.conf.preset == "flex":
            @callback(
                Input(self.f["preset"], "value"),
                State(kid.kmviz("database"), "value"),
                State(self._trace.f.all, "id"),
                Output(self._trace.f.all, "value"),
                State(self._title.f.all, "id"),
                Output(self._title.f.all, "value"),
                State(self._legend.f.all, "id"),
                Output(self._legend.f.all, "value"),
                prevent_initial_call=True
            )
            def update_preset_values(preset, db, ids_map, ids_title, ids_legend):
                if db and preset in self.st.engine.get(db).presets.map:
                    p = self.st.engine.get(db).presets.map[preset]
                    rmap = set_preset_values(ids_map, p.model_dump(exclude=["title", "legend"]))
                    rtitle = set_preset_values(ids_title, p.title.model_dump())
                    rlegend = set_preset_values(ids_legend, p.legend.model_dump())
                    return rmap, rtitle, rlegend
                return (no_update,) * len(ids_map), (no_update,) * len(ids_title), (no_update,) * len(ids_legend)
