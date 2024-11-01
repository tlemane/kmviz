from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color, khide, kshow
from dash_extensions.enrich import html, dcc, callback, Input, Output, State, ctx, no_update
import plotly.graph_objects as go
import plotly.io as pio
from kmviz.ui.utils import icons, make_select_data
from dash.exceptions import PreventUpdate
from dash import Patch
from kmviz.core.log import kmv_debug

from kmviz.ui.id_factory import kid
from kmviz.ui.layouts.figure.plotly import px_options, valid_input, fix_px_params, make_plot_px, to_bool, select_cscale
from kmviz.ui.layouts.figure.title import TitleLayout
from kmviz.ui.layouts.figure.axe import AxesLayout
from kmviz.ui.layouts.figure.legend import LegendLayout
from kmviz.ui.layouts.figure.color import ColorLegendLayout
from kmviz.ui.layouts.figure.shape import ShapeLayout
from kmviz.ui.layouts.figure.download_graph import DownloadGraphLayout
from kmviz.ui.layouts.figure.slider import SliderLayout
from kmviz.ui.layouts.figure import apply_presets
from kmviz.ui.layouts.filter import FilterLayout

from kmviz.ui.components.helpers import from_json
from kmviz.ui.presets import set_preset_values
from kmviz.core.config import state

from dash_iconify import DashIconify

import pandas as pd
from pandas.api.types import is_numeric_dtype

import dash_mantine_components as dmc

class TraceLayout:

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
                cf.multi(self.f("xselect"), [], label="X", clearable=True, searchable=True, value=[], className="kmviz-figure-select", size="xs"),
                cf.multi(self.f("yselect"), [], label="Y", clearable=True, searchable=True, value=[], className="kmviz-figure-select", size="xs"),
                cf.multi(self.f("zselect"), [], label="Z", clearable=True, searchable=True, value=[], className="kmviz-figure-select", size="xs"),
                cf.select(self.f("color"), [], label="Color", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("size"), [], label="Size", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("text"), [], label="Text", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("symbol"), [], label="Symbol", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("pattern_shape"), [], label="Pattern shape", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("base"), [], label="Base", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("line_dash"), [], label="Line dash", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("line_group"), [], label="Line group", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.multi(self.f("dimensions"), [], label="Dimensions", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("values"), [], label="Values", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("names"), [], label="Names", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
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

    def _dist_panel(self):
        return cf.tabs_panel(
            self.f["dist-panel"],
            cf.group(
                self.f["dist-grp-1"],
                cf.select(self.f("violinmode"), ["group", "overlay"], label="Violin mode", value="group", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("boxmode"), ["group", "overlay"], label="Box mode", value="group", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("points"), ["outliers", "suspectedoutliers", "all", "False"], label="Points", value="outliers", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("box"), ["True", "False"], label="Violin box", value="False", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("notched"), ["True", "False"], label="Box notches", value="False",  clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
            ),
            value="dist"
        )

    def _dens_panel(self):
        return cf.tabs_panel(
            self.f["dens-panel"],
            cf.group(
                self.f["dens-grp-1"],
                cf.select(self.f("histfunc"), ["count", "sum", "avg", "min", "max"], label="Hist function", value="count", searchable=True, clearable=True, size="xs", className="kmviz-figure-select"),
                cf.select(self.f("histnorm"), ["percent", "probability", "density", "probability density"], label="Hist norm", value="", searchable=True, clearable=True, size="xs", className="kmviz-figure-select"),
                cf.number(self.f("nbinsx"), label = "X bins", min=0, max=1000, step=1, value=4, icon=icons("integer"), size="xs"),
                cf.number(self.f("nbinsy"), label = "Y bins", min=0, max=1000, step=1, value=4, icon=icons("integer"), size="xs"),
                cf.number(self.f("nbins"), label = "N bins", min=0, max=1000, step=1, value=4, icon=icons("integer"), size="xs"),
                cf.select(self.f("contours_coloring"), ["fill", "heatmap", "lines", "none"], label="Contours coloring", searchable=True, clearable=True, size="xs", className="kmviz-figure-select"),
                cf.segmented(self.f("cumulative"), data=[{"label":"cumulative", "value":"True"}, {"label":"noncumulative", "value":"False"}], value="False", size="xs", className="kmviz-figure-segmented"),
            ),
            value="dens"
        )

    def _facet_panel(self):
        return cf.tabs_panel(
            self.f["facet-panel"],
            cf.group(
                self.f["facet-grp-1"],
                cf.select(self.f("facet_row"), [], label="Row", clearable=True, size="xs", className="kmviz-figure-select"),
                cf.select(self.f("facet_col"), [], label="Column", clearable=True, size="xs", className="kmviz-figure-select"),
                cf.number(self.f("facet_col_wrap"), label="Wrap", min=0, max=10, step=1, value=0, icon=icons("integer"), size="xs"),
                cf.number(self.f("facet_row_spacing"), label="Row spacing", min=0.0, max=1.0, step=0.01, value=0.03, icon=icons("floating"), decimalScale=2, size="xs"),
                cf.number(self.f("facet_col_spacing"), label="Col spacing", min=0.0, max=1.0, step=0.01, value=0.03, icon=icons("floating"), decimalScale=2, size="xs"),
            ),
            value="facet"
        )

    def _marg_panel(self):
        return cf.tabs_panel(
            self.f["marg-panel"],
            cf.group(
                self.f["marg-grp-1"],
                cf.select(self.f("marginal_x"), ["rug", "box", "violin", "histogram"], label="X", clearable=True, className="kmviz-figure-select", size="xs"),
                cf.select(self.f("marginal_y"), ["rug", "box", "violin", "histogram"], label="Y", clearable=True, className="kmviz-figure-select", size="xs"),
            ),
            value="marg"
        )

    def _trend_panel(self):
        return cf.tabs_panel(
            self.f["trend-panel"],
            [
                cf.group(
                    self.f["trend-grp-1"],
                    cf.select(self.f("trendline"), ["ols", "lowess", "rolling", "expanding", "ewm"], label="Type", clearable=True, className="kmviz-figure-select", size="xs"),
                    cf.select(self.f("trendline_scope"), ["trace", "overall"], label="Scope", value="trace", className="kmviz-figure-select", size="xs"),
                ),
                cf.json(self.f("trendline_options"), placeholder="ex: {'value1': 'circle-open', 'value2': 'square-open'}", label="Options", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json")),
            ],
            value="trend"
        )

    def _style_panel(self):
        return cf.tabs_panel(
            self.f["style-panel"],
            [
                cf.group(
                    self.f["style-grp-1"],
                    cf.select(self.f("barmode"), ["relative", "group", "overlay"], label="Bar mode", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                    cf.select(self.f("line_shape"),  ["hv", "vh", "hvh", "vhv", "spline", "linear"], label="Line shape", clearable=True, searchable=True, className="kmviz-figure-select", size="xs"),
                    cf.select(self.f("orientation"), [ { "label": "vertical", "value": "v" }, { "label": "horizontal", "value": "h" } ], label="Orientation", className="kmviz-figure-select", size="xs"),
                    cf.select(self.f("markers"), [ { "label": "Show", "value": "True" }, { "label": "Hide", "value": "False" } ], label="Markers", className="kmviz-figure-select", size="xs")
                ),
                cf.group(
                    self.f["style-grp-2"],
                    cf.select(self.f("template"), list(pio.templates), label="Theme", clearable=True, searchable=True, size="xs", className="kmviz-figure-select", leftSection=icons("style", width=20)),
                    cf.sseqscale(self.f("color_seq_continuous_scale"), label="Color sequential scale", clearable=True, searchable=True, size="xs", className="kmviz-figure-select"),
                    cf.sdivscale(self.f("color_div_continuous_scale"), label="Color diverging scale", clearable=True, searchable=True, size="xs", className="kmviz-figure-select"),
                    cf.scycscale(self.f("color_cyc_continuous_scale"), label="Color cyclical scale", clearable=True, searchable=True, size="xs", className="kmviz-figure-select"),
                    cf.number(self.f("color_continuous_midpoint"), label="Color midpoint", min=None, max=None, step=None, value=None, leftSection=icons("floating"), decimalScale=2, size="xs"),
                    cf.number(self.f("opacity"), label="Opacity", min=0.0, max=1.0, step=0.01, value=0.7, leftSection=icons("floating"), decimalScale=2, size="xs"),
                    cf.number(self.f("size_max"), label="Max size", min=0, max=50, step=1, value=15, leftSection=icons("integer"), decimalScale=2, size="xs"),
                ),
                cf.group(
                    self.f["style-grp-3"],
                    cf.json(self.f("color_discrete_map"), placeholder='ex: {"v1": "blue", "v2": "red"}', label="Color map", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("symbol_map"), placeholder='ex: {"v1": "circle-open", "v2": "square-open"}', label="Symbol map", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("color_discrete_sequence"), placeholder='ex: {"seq": ["red", "blue"] }', label="Color sequence", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("symbol_sequence"), placeholder='ex: {"seq": ["circle-open", "square-open"] }', label="Symbol sequence", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    grow=True,
                ),
                cf.group(
                    self.f["style-grp-4"],
                    cf.json(self.f("pattern_shape_map"), placeholder="ex: {'value1': '+', 'value2': '/'}", label="Pattern shape map", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("pattern_shape_sequence"), placeholder="ex: {'seq': ['+', '/', '-'] }", label="Pattern shape sequence", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("line_dash_map"), placeholder="ex: {'value1': 'dot', 'value2': 'dash'}", label="Line dash map", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    cf.json(self.f("line_dash_sequence"), placeholder="ex: {'seq': ['longdash', 'dashdot', 'longdashdot'] }", label="Line dash sequence", value=None, formatOnBlur=True, maxRows=4, autosize=True, debounce=1, validationError="Invalid json", icon=icons("json"), size="xs"),
                    grow=True
                ),
            ],
            value="style"
        )

    def layout(self):
        ptype = [ "Scatter", "Line", "Area", "Bar", "Parallel categories", "Parallel coordinates", "Scatter matrix", "Density heatmap", "Density contour", "Violin", "Box", "Histogram" ]
        return cf.tabs(
            self.f["tabs"],
            cf.tabs_list(
                self.f["tabslist"],
                cf.select(self.f("type"), ptype, placeholder="Type", leftSection=icons("plot"), className="kmviz-figure-select"),
                cf.tabs_tab(self.f["data-tab"], "Data", value="data"),
                cf.tabs_tab(self.f["anim-tab"], "Animation", value="anim"),
                cf.tabs_tab(self.f["dist-tab"], "Distribution", value="dist"),
                cf.tabs_tab(self.f["dens-tab"], "Density", value="dens"),
                cf.tabs_tab(self.f["facet-tab"], "Facet", value="facet"),
                cf.tabs_tab(self.f["marg-tab"], "Marginal", value="marg"),
                cf.tabs_tab(self.f["trend-tab"], "Trendline", value="trend"),
                cf.tabs_tab(self.f["style-tab"], "Style", value="style"),
            ),
            self._data_panel(),
            self._anim_panel(),
            self._dist_panel(),
            self._dens_panel(),
            self._facet_panel(),
            self._marg_panel(),
            self._trend_panel(),
            self._style_panel(),

            value=None
        )

    def apply_plot_presets(self, params: dict, ptype, X, Y, Z, priority):
        res = dict(X=X, Y=Y, Z=Z, type=ptype)

        for v in ("X", "Y", "Z", "type"):
            if v in params:
                if params[v] is not None:
                    if priority or not len(params[v]):
                        res[v] = params[v]
                del params[v]

        return res["type"], res["X"], res["Y"], res["Z"]

    def callbacks(self):

        @callback(
            Input(self.f("type"), "value"),
            State(self.f.all, "id"),
            Output(self.f.all, "style"),
            prevent_initial_call=True
        )
        def update_constraints(ptype, options):
            if ptype is None:
                return (kshow,) + (khide,) * (len(options)-1)
            out = []

            show = {"display": "inline"}
            hide = {"display": "none"}

            for opt in options:
                if opt["index"] in px_options[ptype]:
                    out.append(show)
                else:
                    out.append(hide)
            return out

        @callback(
            Input(self.fdata, "virtualRowData"),
            Output(self.f("xselect"), "data"),
            Output(self.f("yselect"), "data"),
            Output(self.f("zselect"), "data"),
            Output(self.f("color"), "data"),
            Output(self.f("text"), "data"),
            Output(self.f("symbol"), "data"),
            Output(self.f("animation_frame"), "data"),
            Output(self.f("animation_group"), "data"),
            Output(self.f("facet_row"), "data"),
            Output(self.f("facet_col"), "data"),
            Output(self.f("base"), "data"),
            Output(self.f("pattern_shape"), "data"),
            Output(self.f("line_dash"), "data"),
            Output(self.f("line_group"), "data"),
            Output(self.f("dimensions"), "data"),
            Output(self.f("values"), "data"),
            Output(self.f("names"), "data"),
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

            return (cols,) * 17 + (cols_size,)

        def _blank() -> go.Figure:
            fig = go.Figure(go.Scatter(x=[], y = []))
            fig.update_layout(template = "seaborn")
            return fig

        @callback(
            Output(self.fid, "figure"),
            Input(self.fdata, "virtualRowData"),
            Input(self.f("type"), "value"),
            Input(self.f("xselect"), "value"),
            Input(self.f("yselect"), "value"),
            Input(self.f("zselect"), "value"),
            Input(self.f("size"), "value"),
            Input(self.f("color"), "value"),
            Input(self.f("text"), "value"),
            Input(self.f("symbol"), "value"),
            Input(self.f("animation_frame"), "value"),
            Input(self.f("animation_group"), "value"),
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
            Input(self.f("facet_row"), "value"),
            Input(self.f("facet_col"), "value"),
            Input(self.f("facet_col_wrap"), "value"),
            Input(self.f("facet_row_spacing"), "value"),
            Input(self.f("facet_col_spacing"), "value"),
            Input(self.f("template"), "value"),
            Input(self.f("trendline"), "value"),
            Input(self.f("trendline_scope"), "value"),
            Input(self.f("trendline_options"), "value"),
            Input(self.f("marginal_x"), "value"),
            Input(self.f("marginal_y"), "value"),
            Input(self.f("base"), "value"),
            Input(self.f("pattern_shape"), "value"),
            Input(self.f("orientation"), "value"),
            Input(self.f("pattern_shape_map"), "value"),
            Input(self.f("pattern_shape_sequence"), "value"),
            Input(self.f("barmode"), "value"),
            Input(self.f("line_dash"), "value"),
            Input(self.f("line_group"), "value"),
            Input(self.f("line_shape"), "value"),
            Input(self.f("line_dash_sequence"), "value"),
            Input(self.f("line_dash_map"), "value"),
            Input(self.f("markers"), "value"),
            Input(self.f("dimensions"), "value"),
            Input(self.f("values"), "value"),
            Input(self.f("names"), "value"),
            Input(self.f("histnorm"), "value"),
            Input(self.f("histfunc"), "value"),
            Input(self.f("nbinsx"), "value"),
            Input(self.f("nbinsy"), "value"),
            Input(self.f("boxmode"), "value"),
            Input(self.f("violinmode"), "value"),
            Input(self.f("points"), "value"),
            Input(self.f("notched"), "value"),
            Input(self.f("box"), "value"),
            Input(self.f("contours_coloring"), "value"),
            Input(self.f("cumulative"), "value"),
            Input(self.f("nbins"), "value"),
            State(kid.store["session-id"], "data"),
            State(kid.kmviz("database"), "value"),
            Input(self.preset, "value"),
            prevent_initial_call=True
        )
        def make_plot(data, ptype, X, Y, Z,
                      size, color, text, symbol, animation_frame, animation_group,
                      cscs, cdcs, cccs, ccm, sm, ss, cdm, cds, opacity, size_max,
                      frow, fcol, fcolw, frows, fcols, template,
                      trendline, trendline_scope, trendline_opt, mx, my,
                      base, pattern_shape, orientation, ps_map, ps_seq, barmode,
                      line_dash, line_group, line_shape, ld_seq, ld_map, markers,
                      dimensions, values, names, histn, histf, binx, biny,
                      boxmode, violinmode, points, notched, box, contours_coloring,
                      cumulative, nbins,
                      session, database, preset):

            if not data:
                raise PreventUpdate

            kmv_debug(f"{session}: 'update_plot' triggered by '{ctx.triggered_id}'")

            df = pd.DataFrame.from_dict(data)

            markers = to_bool(markers)
            notched = to_bool(notched)
            box = to_bool(box)
            points = to_bool(points)
            cumulative = to_bool(cumulative)

            scale = select_cscale([cscs, cdcs, cccs])

            params = {
                "size": size,
                "color": color,
                "text": text,
                "symbol": symbol,
                "base": base,
                "pattern_shape": pattern_shape,
                "pattern_shape_sequence": from_json(ps_seq, "seq"),
                "pattern_shape_map": from_json(ps_map),
                "orientation": orientation,
                "barmode": barmode,
                "animation_frame": animation_frame,
                "animation_group": animation_group,
                "color_continuous_midpoint": ccm,
                "color_continuous_scale": scale,
                "symbol_map": from_json(sm),
                "symbol_sequence": from_json(ss, "seq"),
                "color_discrete_map": from_json(cdm),
                "color_discrete_sequence": from_json(cds, "seq"),
                "opacity": opacity,
                "size_max": size_max,
                "facet_row": frow,
                "facet_col": fcol,
                "facet_col_wrap": fcolw,
                "facet_row_spacing": frows,
                "facet_col_spacing": fcols,
                "template": template,
                "marginal_x": mx,
                "marginal_y": my,
                "trendline": trendline,
                "trendline_scope": trendline_scope,
                "trendline_options": from_json(trendline_opt),
                "line_dash": line_dash,
                "line_group": line_group,
                "line_shape": line_shape,
                "line_dash_sequence": from_json(ld_seq, "seq"),
                "line_dash_map": from_json(ld_map),
                "markers": markers,
                "dimensions": dimensions,
                "values": values,
                "names": names,
                "histnorm": histn,
                "histfunc": histf,
                "nbinsx": binx,
                "nbinsy": biny,
                "boxmode": boxmode,
                "violinmode": violinmode,
                "points": points,
                "notched": notched,
                "box": box,
                "contours_coloring": contours_coloring,
                "nbins": nbins,
                "cumulative": cumulative
            }

            if self.st.conf.preset == "fixed":
                if preset and preset in self.st.engine.get(database).presets.plot:
                    presets = self.st.engine.get(database).presets.plot

                    presets_params = presets[preset].model_dump()

                    ptype, X, Y, Z, = self.apply_plot_presets(presets_params, ptype, X, Y, Z, self.st.engine.get(database).presets.priority)
                    params = apply_presets(presets_params, params, self.st.engine.get(database).presets.priority)

            if not preset and not ptype:
                return _blank()

            valid_input(ptype, X, Y, Z)
            params = fix_px_params(params, ptype)
            return make_plot_px(ptype, df, X, Y, Z, params)

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

                if not len(sdata["points"]):
                    raise PreventUpdate

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
            def on_click_data_plot(value):
                sample = value["points"][0]["hovertext"]

                p = Patch()
                p["ID"] = {'filterType': 'text', 'type': 'equals', 'filter': sample}

                return sample, p, "sequence"

class PlotLayout:
    def __init__(self, st: state, factory, figure_id, figure_data):
        self.st = st
        self.f = factory
        self.fid = figure_id
        self.fdata = figure_data

        self._trace = TraceLayout(self.st, self.f.new("trace"), self.fid, self.fdata, self.f["preset"])
        self._title = TitleLayout(self.f.new("title"), self.fid)
        self._axes = AxesLayout(self.f.new("axes"), self.fid)
        self._slider = SliderLayout(self.f.new("slider"), self.fid, self._axes.x.f("axis-index"))
        self._legend = LegendLayout(self.f.new("legend"), self.fid)
        self._clegend = ColorLegendLayout(self.f.new("clegend"), self.fid)
        self._shape = ShapeLayout(self.f.new("shape"), self.fid)
        self._dl = DownloadGraphLayout(self.f.new("download"), self.fid, "plot")
        self._filter = FilterLayout(self.f.new("filter"), self.fdata)

    def _blank(self) -> go.Figure:
        fig = go.Figure(go.Scatter(x=[], y = []))
        fig.update_layout(template = "seaborn")
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
                cf.tabs_tab(self.f["slider-tab"], "Slider", value="slider"),
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
            cf.tabs_panel(self.f["slider-panel"], self._slider.layout(), value="slider"),
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
        self._shape.callbacks()
        self._dl.callbacks()
        self._slider.callbacks()
        self._clegend.callbacks()
        self._filter.callbacks()

        @callback(
            Input(self.f["rmf"], "n_clicks"),
            Output(self.fdata, "filterModel")
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

            if presets.plot:
                return make_select_data(list(presets.plot.keys())), kshow, presets.defaults.plot
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
            def update_preset_values(preset, db, ids_plot, ids_title, ids_legend):
                if db and preset in self.st.engine.get(db).presets.plot:
                    p = self.st.engine.get(db).presets.plot[preset]
                    rplot = set_preset_values(ids_plot, p.model_dump(exclude=["title", "legend"]))
                    rtitle = set_preset_values(ids_title, p.title.model_dump())
                    rlegend = set_preset_values(ids_legend, p.legend.model_dump())
                    return rplot, rtitle, rlegend
                return (no_update,) * len(ids_plot), (no_update,) * len(ids_title), (no_update,) * len(ids_legend)
