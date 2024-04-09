from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, ctx, callback, clientside_callback
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash
from dash import Patch, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from pandas.api.types import is_numeric_dtype
from kmviz.ui import state
from kmviz.ui.utils import prevent_update_on_none, make_select_data
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.select import kgsf
from kmviz.ui.components.store import ksf
from kmviz.ui.components.figure import from_json, make_plot_px, make_plot, make_plot_callbacks, blank_figure
from kmviz.ui.components.figure import apply_presets, px_options, fix_px_params
from kmviz.ui.layouts.sequence import kseq
from kmviz.ui.layouts.table import ktable
from kmviz.core.log import kmv_debug

kplot = kf.child("plot")

def make_plot_layout():
    return make_plot(kplot)

def make_plot_layout_callbacks():

    make_plot_callbacks(kplot)
    ktrace = kplot.child("trace")


    @callback(
        Input(kplot.sid("rmf"), "n_clicks"),
        Output(ktable.sid("grid"), "filterModel")
    )
    def remove_table_filters(n_clicks):
        if n_clicks:
            return {}
        prevent_update_on_none(None)

    @callback(
        Input(ktable.sid("grid"), "virtualRowData"),
        Output(ktrace("xselect"), "data"),
        Output(ktrace("yselect"), "data"),
        Output(ktrace("zselect"), "data"),
        Output(ktrace("size"), "data"),
        Output(ktrace("color"), "data"),
        Output(ktrace("text"), "data"),
        Output(ktrace("symbol"), "data"),
        Output(ktrace("animation_frame"), "data"),
        Output(ktrace("animation_group"), "data"),
        Output(ktrace("facet_row"), "data"),
        Output(ktrace("facet_col"), "data"),
        Output(ktrace("base"), "data"),
        Output(ktrace("pattern_shape"), "data"),
        Output(ktrace("line_dash"), "data"),
        Output(ktrace("line_group"), "data"),
        Output(ktrace("dimensions"), "data"),
        Output(ktrace("values"), "data"),
        Output(ktrace("names"), "data"),
        Output(kplot.sid("panel"), "disabled"),
        prevent_initial_callbacks=True
    )
    def updateXY(data):
        if not data:
            prevent_update_on_none(None)

        df = pd.DataFrame.from_dict(data)
        cols = make_select_data(list(df))
        cols_size = []
        for c in list(df):
            if is_numeric_dtype(df[c]):
                if all(x >= 0 for x in df[c]):
                    cols_size.append(c)

        return (cols, cols, cols, cols_size, cols, cols, cols, cols,
                cols, cols, cols, cols, cols, cols, cols, cols, cols, cols, False)

    # Takes some time to apply, same behavior with a clientside callback
    @callback(
        Input(ktrace("type"), "value"),
        State(ktrace.all, "id"),
        Output(ktrace.all, "style"),
    )
    def update_constraints(ptype, options):
        show = {"display": "inline"}
        hide = {"display": "none"}
        if ptype is None:
            return [show] + [hide for _ in range(len(options)-1)]

        output = []
        for option in options:
            if option["index"] in px_options[ptype]:
                output.append(show)
            else:
                output.append(hide)
        return output

    @callback(
        Output(kplot.sid("figure"), "figure"),
        Input(ktable.sid("grid"), "virtualRowData"),
        Input(ktrace("type"), "value"),
        Input(ktrace("xselect"), "value"),
        Input(ktrace("yselect"), "value"),
        Input(ktrace("zselect"), "value"),
        Input(ktrace("size"), "value"),
        Input(ktrace("color"), "value"),
        Input(ktrace("text"), "value"),
        Input(ktrace("symbol"), "value"),
        Input(ktrace("animation_frame"), "value"),
        Input(ktrace("animation_group"), "value"),
        Input(ktrace("color_seq_continuous_scale"), "value"),
        Input(ktrace("color_div_continuous_scale"), "value"),
        Input(ktrace("color_cyc_continuous_scale"), "value"),
        Input(ktrace("color_continuous_midpoint"), "value"),
        Input(ktrace("symbol_map"), "value"),
        Input(ktrace("symbol_sequence"), "value"),
        Input(ktrace("color_discrete_map"), "value"),
        Input(ktrace("color_discrete_sequence"), "value"),
        Input(ktrace("opacity"), "value"),
        Input(ktrace("size_max"), "value"),
        Input(ktrace("facet_row"), "value"),
        Input(ktrace("facet_col"), "value"),
        Input(ktrace("facet_col_wrap"), "value"),
        Input(ktrace("facet_row_spacing"), "value"),
        Input(ktrace("facet_col_spacing"), "value"),
        Input(ktrace("template"), "value"),
        Input(ktrace("trendline"), "value"),
        Input(ktrace("trendline_scope"), "value"),
        Input(ktrace("trendline_options"), "value"),
        Input(ktrace("marginal_x"), "value"),
        Input(ktrace("marginal_y"), "value"),
        Input(ktrace("base"), "value"),
        Input(ktrace("pattern_shape"), "value"),
        Input(ktrace("orientation"), "value"),
        Input(ktrace("pattern_shape_map"), "value"),
        Input(ktrace("pattern_shape_sequence"), "value"),
        Input(ktrace("barmode"), "value"),
        Input(ktrace("line_dash"), "value"),
        Input(ktrace("line_group"), "value"),
        Input(ktrace("line_shape"), "value"),
        Input(ktrace("line_dash_sequence"), "value"),
        Input(ktrace("line_dash_map"), "value"),
        Input(ktrace("markers"), "value"),
        Input(ktrace("dimensions"), "value"),
        Input(ktrace("values"), "value"),
        Input(ktrace("names"), "value"),
        Input(ktrace("histnorm"), "value"),
        Input(ktrace("histfunc"), "value"),
        Input(ktrace("nbinsx"), "value"),
        Input(ktrace("nbinsy"), "value"),
        Input(ktrace("boxmode"), "value"),
        Input(ktrace("violinmode"), "value"),
        Input(ktrace("points"), "value"),
        Input(ktrace("notched"), "value"),
        Input(ktrace("box"), "value"),
        Input(ktrace("contours_coloring"), "value"),
        Input(kplot.sid("select-preset"), "value"),
        State(kgsf("provider"), "value"),
        State(kf.sid("session-id"), "data"),
        prevent_initial_callbacks=True
    )
    def update_plot(data, ptype, X, Y, Z,
                    size, color, text, symbol, animation_frame, animation_group,
                    cscs, cdcs, cccs, ccm, sm, ss, cdm, cds, opacity, size_max,
                    frow, fcol, fcolw, frows, fcols, template,
                    trendline, trendline_scope, trendline_opt, mx, my,
                    base, pattern_shape, orientation, ps_map, ps_seq, barmode,
                    line_dash, line_group, line_shape, ld_seq, ld_map, markers,
                    dimensions, values, names, histn, histf, binx, biny,
                    boxmode, violinmode, points, notched, box, contours_coloring,
                    preset_name, provider, session):

        kmv_debug(f"{session}: 'update_plot' triggered by '{ctx.triggered_id}'")

        if not data:
            prevent_update_on_none(data)

        df = pd.DataFrame.from_dict(data)

        markers = True if markers == "True" else False
        notched = True if notched == "True" else False
        box = True if box == "True" else False
        points = False if points == "False" else points

        scales = [cscs, cdcs, cccs]
        scale=None
        if any(scales):
            scale = next(s for s in scales if s is not None)

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
            "contours_coloring": contours_coloring
        }

        if preset_name:
            presets = state.kmstate.providers.get(provider).presets["plot"][preset_name].copy()
            priority = presets["priority"]
            del presets["priority"]
            del presets["name"]

            if "X" in presets:
                if priority or not len(X):
                    X = presets["X"]
                del presets["X"]

            if "Y" in presets:
                if priority or not len(Y):
                    Y = presets["Y"]
                del presets["Y"]

            if "Z" in presets:
                if priority or not len(Z):
                    Z = presets["Z"]
                del presets["Z"]

            if "type" in presets:
                if priority or ptype is None:
                    ptype = presets["type"]
                del presets["type"]
            params = apply_presets(presets, params, priority)

        if ptype not in {"Parallel coordinates", "Parallel categories", "Pie", "Scatter matrix"}:
            prevent_update_on_none(X, Y)
            if not len(X) or not len(Y):
                prevent_update_on_none(None)

        if ptype in {"Density heatmap", "Density contour"}:
            prevent_update_on_none(Z)
            if not len(Z):
                prevent_update_on_none(None)

        prevent_update_on_none(ptype)

        params = fix_px_params(params, ptype)

        return make_plot_px(ptype, df, X, Y, Z, params)

    @callback(
        Input(kplot.sid("figure"), "selectedData"),
        State(kgsf("query"), "value"),
        State(kgsf("provider"), "value"),
        State(ksf("query-results"), "data"),
        Output(ktable.sid("grid"), "filterModel"),
        prevent_initial_callbacks=True
    )
    def on_selected(sdata, query, provider, query_result):

        qr = query_result[query][provider]
        conditions = []

        if not len(sdata["points"]):
            prevent_update_on_none(None)

        for data in sdata["points"]:
            conditions.append(
                    {"filter": data["hovertext"], "filterType":"text", "type":"equals"}
            )

        p = Patch()
        p["ID"] = { "filterType": "text", "operator":"OR", "conditions": conditions }
        return p


    if not state.kmstate.plot_only:
        @callback(
            Input(kplot.sid("figure"), "clickData"),
            State(kgsf("query"), "value"),
            State(kgsf("provider"), "value"),
            State(ksf("query-results"), "data"),
            Output(kseq.sid("select"), "value"),
            Output(ktable.sid("grid"), "filterModel"),
            Output("tab-select", "value"),
            prevent_initial_callbacks=True
        )
        def on_click(data, query, provider, query_result):

            qr = query_result[query][provider]
            sample = data["points"][0]["hovertext"]

            p = Patch()
            p["ID"] = {'filterType': 'text', 'type': 'equals', 'filter': sample}
            return sample, p, "sequence"


