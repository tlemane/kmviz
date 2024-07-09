from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, callback
import dash_mantine_components as dmc
from dash import no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

from dash_iconify import DashIconify

from kmviz.ui.utils import make_select_data, prevent_update_on_none, KMVIZ_ICONS
from kmviz.ui.components.figure import make_plot_title, make_plot_title_callbacks, make_select_input, make_hover_color_picker
from kmviz.ui.components.figure import make_axes, make_plot_legend, make_plot_shape
from kmviz.ui.components.figure import make_axes_callbacks, make_plot_legend_callbacks, make_plot_shape_callbacks
from kmviz.ui.components.select import kgsf
from kmviz.ui.components.store import ksf
from kmviz.ui.layouts.table import ktable

from kmviz.ui.id_factory import kmviz_factory as kf
import dash_bio as dashbio

import itertools
import operator
import random
import statistics

import warnings
warnings.filterwarnings('ignore', module='gradpyent')
from gradpyent import gradient
from gradpyent.library.formats import get_verified_color

kseq = kf.child("seq")

def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = "seaborn")
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig

def make_coverage(cov: list, abs, start, end):
    grad = gradient.Gradient(gradient_start=start, gradient_end=end)

    ranges = []
    series = []

    coverage = []
    legend = []

    for r in itertools.groupby(enumerate(cov), key=operator.itemgetter(1)):
        series.append(r[0])
        L = list(r[1])
        ranges.append((L[0][0], L[-1][0] + 1))

    colors = grad.get_gradient_series(series, fmt="html")

    for i, c in enumerate(colors):
        coverage.append({
            "bgcolor": c,
            "start": ranges[i][0],
            "end": ranges[i][1],
            "tooltip": round(series[i], 2),
            "onclick": round(series[i], 2),
        })

    if all(isinstance(a, int) for a in series):
        sorted_series = sorted(zip(series, colors))

        s = set()
        for value, color in sorted_series:
            if value not in s:
                legend.append({
                    "color": color,
                    "name": value
                })
                s.add(value)

    else:
        legend.append({
            "color": colors[min((val, idx) for (idx, val) in enumerate(series))[1]],
            "name": round(min(series), 2)
        })
        legend.append({
            "color": colors[max((val, idx) for (idx, val) in enumerate(series))[1]],
            "name": round(max(series), 2)
        })


    return coverage, legend

def make_sequence_layout():

    down_select = dmc.SegmentedControl(
        id=kseq.sid("down-select"),
        data=make_select_data(["png", "jpg", "svg", "pdf", "html", "json"]),
        value="png",
        size="xs",
        color=dmc.theme.DEFAULT_COLORS["dark"][0]
    )

    graph_view = html.Div([
        dmc.Space(h=5),
        dcc.Graph(
            figure=blank_figure(),
            id=kseq.sid("figure"),
            responsive=True,
            style = { "margin-left": "auto", "margin-right": "auto", "height": "50vh", "width": "95%" }
        ),

        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab("Title", value="title"),
                dmc.Tab("Axes", value="axes"),
                dmc.Tab("Legend", value="legend"),
                dmc.Tab("Shape", value="shape"),
                dmc.Group([
                    down_select,
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:download", width=20),
                        id=kseq.sid("down-button"),
                        variant="filled",
                        color = "#1C7ED6",
                    ),
                ], style = {"margin-left":"10px", "width": "fit-content"}, spacing=5),
            ]),
            dmc.TabsPanel(make_plot_title(kseq.child("title")), value="title"),
            dmc.TabsPanel(make_axes(kseq.child("axes")), value="axes"),
            dmc.TabsPanel(make_plot_legend(kseq.child("legend")), value="legend"),
            dmc.TabsPanel(make_plot_shape(kseq.child("shape")), value="shape"),
        ]),

        dcc.Download(id=kseq.sid("download")),
    ])

    seq_view = html.Div([
        dmc.Space(h=10),
        dmc.Group([
            dmc.SegmentedControl(
                id=kseq.sid("mode-select"),
                data=make_select_data(["base", "kmer"]),
                value="base",
                color=dmc.theme.DEFAULT_COLORS["dark"][0],
                size="xs"
            ),
            make_hover_color_picker(
                kseq("start-color"),
                "Min",
                icon=KMVIZ_ICONS["cback"],
                color=dict(hex="#E0DFDF")
            ),
            make_hover_color_picker(
                kseq("end-color"),
                "Max",
                icon=KMVIZ_ICONS["cback"],
                color=dict(hex="#FF0000")
            )
        ]),

        dmc.Space(h=10),

        html.Div([
            dashbio.SequenceViewer(
                id=kseq.sid("seq-view"),
                wrapAminoAcids=True,
                toolbar=False,
                search=False,
                badge=False,
                charsPerLine=130,
                sequenceMaxHeight="55vh",
            ),
        ], style = { "margin-left": "auto", "margin-right": "auto", "position":"relative" })

    ], style={"margin-left": "20px"})

    tabs = dmc.Tabs([
        dmc.TabsList([
            dmc.Tab("Graph view", value="graph", icon=DashIconify(icon="mdi:graph-line")),
            dmc.Tab("Sequence view", value="sequence", icon=DashIconify(icon="mdi:dna")),
            dmc.Group([
                dmc.Select(
                    id=kseq.sid("select"),
                    size="xs",
                    icon=DashIconify(icon="mingcute:document-fill"),
                    className="kmviz-gselect"
                ),
                dmc.ActionIcon(
                    DashIconify(icon="bi:filetype-json", width=20),
                    id=kseq.sid("down-data-button"),
                    variant="filled",
                    color = "#1C7ED6"
                ),
                dcc.Download(id=kseq.sid("download-data")),
            ]),
        ]),

        dmc.TabsPanel(graph_view, value="graph"),
        dmc.TabsPanel(seq_view, value="sequence"),
    ], value = "graph")

    return tabs

def to_bio_color(c):
    if not c:
        return c
    if "rgb" in c:
        m = c["rgb"]
        return [m["r"], m["g"], m["b"]]
    elif "hex" in c:
        return c["hex"]
    return c

def make_sequence_layout_callbacks():

    @callback(
        Input(kseq.sid("down-button"), "n_clicks"),
        State(kseq.sid("down-select"), "value"),
        State(kseq.sid("figure"), "figure"),
        Output(kseq.sid("download"), "data"),
        prevent_initial_call=True,
    )
    def download_cov(n_clicks, fmt, data):
        if n_clicks:
            if fmt == "html":
                content = pio.to_html(data, validate=False)
                return dict(content=content, filename="kmviz-cov.html")
            elif fmt == "json":
                content = pio.to_json(data, validate=False)
                return dict(content=content, filename="kmviz-cov.json")
            else:
                content = pio.to_image(data, fmt, validate=False)
                return dcc.send_bytes(content, f"kmviz-cov.{fmt}")

    @callback(
        Input(kseq.sid("down-data-button"), "n_clicks"),
        State(kgsf("provider"), "value"),
        State(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("download-data"), "data"),
        prevent_initial_call=True,
    )
    def download_json(n_clicks, provider, query, query_result):
        if n_clicks:
            if provider.startswith("__kmviz_df"):
                prevent_update_on_none(None)

            prevent_update_on_none(provider, query)

            qr = query_result[query][provider]

            res = {}
            res[query] = {}

            for sample, resp in qr.response.items():
                if resp.has_abs():
                    res[query][sample] = {"ykmer": resp.covyk, "ybase": resp.covyb}
                else:
                    res[query][sample] = {"xkmer": resp.covxk, "xbase": resp.covxb}

            return dict(content=str(res), filename=f"{provider}-{query}.json")

    @callback(
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("select"), "data"),
        Output(kseq.sid("select"), "value"),
        Output(kseq.sid("panel"), "disabled"),
        prevent_initial_call=True,
    )
    def update_sample_select(provider, query, query_result):
        prevent_update_on_none(provider, query)

        if provider.startswith("__kmviz_df"):
            prevent_update_on_none(None)

        qr = query_result[query][provider]
        ids = list(qr.df["ID"])
        if not ids:
            return no_update, no_update, True
        return make_select_data(ids), ids[0], False

    @callback(
        Input(ktable.sid("grid"), "selectedRows"),
        Output(kseq.sid("select"), "value"),
        Output("tab-select", "value"),
        prevent_initial_call=True
    )
    def on_selected(data):
        if not len(data):
            prevent_update_on_none(None)

        return data[0]["ID"], "sequence"

    @callback(
        Input(kseq.sid("select"), "value"),
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("figure"), "figure"),
        Output(kseq.sid("select"), "value"),
        prevent_initial_call=True,
    )
    def update_sequence_graph(sample, provider, query, query_result):
        if provider.startswith("__kmviz_df"):
            prevent_update_on_none(None)

        prevent_update_on_none(sample, provider, query)

        qr = query_result[query][provider]

        if sample not in qr.response:
            sample = list(qr.df["ID"])[0]

        f = {'ID': {'filterType': 'text', 'type': 'contains', 'filter': sample}}

        index = list(range(len(qr.query.seq)))

        m = []
        cols = ["base"]

        if qr.response[sample].k:
            m = [None] * (qr.response[sample].k-1)
            cols = ["kmer", "base"]

        if qr.response[sample].has_abs():
            df = pd.DataFrame({"Sequence": index, "kmer": qr.response[sample].covyk + m, "base": qr.response[sample].covyb})
            fig = px.line(df, x="Sequence", y=cols, line_shape="linear", markers=True)
        else:
            df = pd.DataFrame({"Sequence": index, "kmer": qr.response[sample].covxk + m, "base": qr.response[sample].covxb})
            fig = px.line(df, x="Sequence", y=cols, line_shape="linear", markers=True)

        fig.update_layout(
            xaxis = dict(
                tickmode = 'array',
                tickvals = index,
                ticktext = [x for x in qr.query.seq]
            )
        )

        fig.update_layout(
            xaxis=dict(rangeslider=dict(visible=True,range=[0, len(qr.query.seq)]),
                       range=[0, 50],
                       type="category")
        )

        fig.update_layout(legend_title_text="")
        fig.update_xaxes(title_text="Sequence")
        fig.update_yaxes(rangemode="tozero")

        return fig, sample

    @callback(
        Input(kseq.sid("select"), "value"),
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        Input(kseq.sid("mode-select"), "value"),
        Input(kseq("start-color"), "value"),
        Input(kseq("end-color"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("seq-view"), "sequence"),
        Output(kseq.sid("seq-view"), "coverage"),
        Output(kseq.sid("seq-view"), "legend"),
        Output(kseq.sid("select"), "value"),
        prevent_initial_call=True,
    )
    def update_sequence_view(sample, provider, query, mode, start, end, query_result):
        if provider.startswith("__kmviz_df"):
            prevent_update_on_none(None)
        prevent_update_on_none(sample, provider, query)

        qr = query_result[query][provider]

        cov_type = "base"

        if sample not in qr.response:
            sample = list(qr.df["ID"])[0]

        if mode == "kmer" and not qr.response[sample].k:
            mode == "base"

        start = to_bio_color(start)
        end = to_bio_color(end)

        if qr.response[sample].has_abs():
            cov, leg = make_coverage(qr.response[sample].covyb if mode == "base" else qr.response[sample].covyk, True, start, end)
        else:
            cov, leg = make_coverage(qr.response[sample].covxb if mode == "base" else qr.response[sample].covxk, False, start, end)

        return qr.query.seq, cov, leg, sample

    make_plot_title_callbacks(kseq.child("title"), kseq.sid("figure"))
    make_axes_callbacks(kseq.child("axes"), kseq.sid("figure"))
    make_plot_legend_callbacks(kseq.child("legend"), kseq.sid("figure"))
    make_plot_shape_callbacks(kseq.child("shape"), kseq.sid("figure"))

