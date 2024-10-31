from kmviz.ui.id_factory import kid
from kmviz.core.config import state
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color
from dash_extensions.enrich import html, dcc
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import dash_bio as dashbio
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import html, Input, State, Output, callback, no_update
from kmviz.ui.utils import prevent_update_on_none, make_select_data
from kmviz.ui.layouts.figure.title import TitleLayout
from kmviz.ui.layouts.figure.axe import AxesLayout
from kmviz.ui.layouts.figure.legend import LegendLayout
from kmviz.ui.layouts.figure.shape import ShapeLayout
from kmviz.ui.layouts.figure.slider import SliderLayout
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import warnings
warnings.filterwarnings('ignore', module='gradpyent')

import itertools
import operator
from gradpyent import gradient

class SequenceGraphViewLayout:
    def __init__(self, st: state):
        self.st = state
        self.figure = kid.sequence.new("figure")

        self._title = TitleLayout(self.figure.new("title"), kid.sequence["figure"])
        self._axes = AxesLayout(self.figure.new("axes"), kid.sequence["figure"])
        self._legend = LegendLayout(self.figure.new("legend"), kid.sequence["figure"])
        self._shapes = ShapeLayout(self.figure.new("shape"), kid.sequence["figure"])
        self._slider = SliderLayout(self.figure.new("slider"), kid.sequence["figure"], self._axes.x.f("axis-index"))

    def _blank(self):
        fig = go.Figure(go.Scatter(x=[], y=[]))
        fig.update_layout(template="seaborn")
        fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
        fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
        return fig

    def layout(self) -> html.Div:
        return cf.div(
            kid.sequence["graph"],
            dcc.Graph(
                figure=self._blank(),
                id=kid.sequence["figure"],
                responsive=True,
                className="kmviz-dcc-sequence-graph",
            ),
            cf.tabs(
                kid.sequence["graph-tabs"],
                cf.tabs_list(
                    kid.sequence["graph-tabslist"],
                    cf.tabs_tab(kid.sequence["graph-title-tab"], "Title", "title"),
                    cf.tabs_tab(kid.sequence["graph-axes-tab"], "Axes", "axes"),
                    cf.tabs_tab(kid.sequence["graph-slider-tab"], "Slider", "slider"),
                    cf.tabs_tab(kid.sequence["graph-legend-tab"], "Legend", "legend"),
                    cf.tabs_tab(kid.sequence["graph-shape-tab"], "Shape", "shape"),
                ),
                cf.tabs_panel(kid.sequence["graph-title-panel"], self._title.layout(), "title"),
                cf.tabs_panel(kid.sequence["graph-axes-panel"], self._axes.layout(), "axes"),
                cf.tabs_panel(kid.sequence["graph-slider-panel"], self._slider.layout(), "slider"),
                cf.tabs_panel(kid.sequence["graph-legend-panel"], self._legend.layout(), "legend"),
                cf.tabs_panel(kid.sequence["graph-shape-panel"], self._shapes.layout(), "shape"),
                value="title"
            )
        )

    def callbacks(self) -> None:

        @callback(
            Input(kid.sequence["sample"], "value"),
            Input(kid.kmviz("database"), "value"),
            Input(kid.kmviz("query"), "value"),
            State(kid.store["results"], "data"),
            Output(kid.sequence["figure"], "figure"),
            Output(kid.sequence["sample"], "value"),
            prevent_initial_call=True
        )
        def update_graph_view(sample, db, query, results):
            if not db or not query or db.startswith("__kmviz_df"):
                raise PreventUpdate

            qr = results[query][db]

            if qr.df.empty:
                raise PreventUpdate

            if sample not in qr.response:
                sample = list(qr.df["ID"])[0]

            f = {"ID": {"filterType": "text", "type": "contains", "filter": sample}}

            index = list(range(len(qr.query.seq)))

            m = []
            cols = ["base"]

            if qr.response[sample].k:
                m = [None] * (qr.response[sample].k - 1)
                cols = ["kmer", "base"]

            if qr.response[sample].has_abs():
                if qr.response[sample].covyk is None:
                    raise PreventUpdate
                df = pd.DataFrame({"Sequence": index, "kmer": qr.response[sample].covyk + m, "base": qr.response[sample].covyb})
                fig = px.line(df, x="Sequence", y=cols, line_shape="linear", markers=True)
            else:
                if qr.response[sample].covxk is None:
                    raise PreventUpdate
                df = pd.DataFrame({"Sequence": index, "kmer": qr.response[sample].covxk + m, "base": qr.response[sample].covxb})
                fig = px.line(df, x="Sequence", y=cols, line_shape="linear", markers=True)

            fig.update_layout(
                xaxis = dict(
                    tickmode = "array",
                    tickvals = index,
                    ticktext = [x for x in qr.query.seq]
                )
            )

            fig.update_layout(
                xaxis = dict(rangeslider=dict(visible=True, range=[0, len(qr.query.seq)]),
                             range=[0, 50],
                             type="category")
            )

            fig.update_layout(legend_title_text="")
            fig.update_xaxes(title_text="Sequence")
            fig.update_yaxes(rangemode="tozero")

            return fig, sample

        self._title.callbacks()
        self._axes.callbacks()
        self._legend.callbacks()
        self._shapes.callbacks()
        self._slider.callbacks()

class SequenceTextViewLayout:
    def __init__(self, st: state):
        self.st = st

    def _make_coverage(self, cov: list, abs, start, end):
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

    def layout(self) -> html.Div:
        return cf.div(
            kid.sequence["text"],
            dmc.Space(h=10),
            cf.group(
                kid.sequence["text-grp"],
                cf.segmented(
                    kid.sequence["text-mode"],
                    data=["base", "kmer"],
                    value="base",
                    color=km_color,
                    size="xs",
                    className = "kmviz-figure-segmented"
                ),
                cf.color(
                    kid.sequence["start"],
                    label="Min color",
                    size="xs",
                    leftSection=DashIconify(icon="cil:paint"),
                    withPreview=False,
                    value="#E0DFDF",
                    noTranspa=True,
                ),
                cf.color(
                    kid.sequence["end"],
                    label="Max color",
                    size="xs",
                    leftSection=DashIconify(icon="cil:paint"),
                    withPreview=False,
                    value=km_color,
                    noTranspa=True,
                )
            ),

            cf.div(
                kid.sequence["view-div"],
                dashbio.SequenceViewer(
                    id=kid.sequence["view"],
                    wrapAminoAcids=True,
                    toolbar=False,
                    search=False,
                    badge=False,
                    charsPerLine=130,
                    sequenceMaxHeight="55vh"
                ),
                style = { "margin-left": "auto", "margin-right": "auto", "position": "relative"}
            )
        )

    def callbacks(self) -> None:

        @callback(
            Input(kid.sequence["sample"], "value"),
            Input(kid.kmviz("database"), "value"),
            Input(kid.kmviz("query"), "value"),
            Input(kid.sequence["text-mode"], "value"),
            Input(kid.sequence["start"], "value"),
            Input(kid.sequence["end"], "value"),
            State(kid.store["results"], "data"),
            Output(kid.sequence["view"], "sequence"),
            Output(kid.sequence["view"], "coverage"),
            Output(kid.sequence["view"], "legend"),
            Output(kid.sequence["sample"], "value"),
            prevent_initial_call=True
        )
        def update_text_view(sample, db, query, mode, start, end, results):
            if not db or not query or db.startswith("__kmviz_df"):
                raise PreventUpdate
            prevent_update_on_none(sample, db, query)

            qr = results[query][db]

            if qr.df.empty:
                raise PreventUpdate

            if sample not in qr.response:
                sample = list(qr.df["ID"])[0]

            if mode == "kmer" and not qr.response[sample].k:
                mode = "base"

            if qr.response[sample].has_abs():
                if qr.response[sample].covyk is None:
                    raise PreventUpdate
                cov, leg = self._make_coverage(qr.response[sample].covyb if mode == "base" else qr.response[sample].covyk, True, start, end)
            else:
                if qr.response[sample].covxk is None:
                    raise PreventUpdate
                cov, leg = self._make_coverage(qr.response[sample].covxb if mode == "base" else qr.response[sample].covxk, True, start, end)

            return qr.query.seq, cov, leg, sample

class SequenceLayout:
    def __init__(self, st: state):
        self.st = st
        self._text = SequenceTextViewLayout(self.st)
        self._graph = SequenceGraphViewLayout(self.st)

    def layout(self):
        return cf.tabs(
                kid.sequence["tabs"],
                cf.tabs_list(
                    kid.sequence["tabslist"],
                    cf.tabs_tab(kid.sequence["graph-view"], "Graph view", value="graph", leftSection=DashIconify(icon="mdi:graph-line")),
                    cf.tabs_tab(kid.sequence["text-view"], "Text view", value="text", leftSection=DashIconify(icon="mdi:dna")),
                    dmc.Space(w=10),
                    cf.group(
                        kid.sequence["tab-head-grp"],
                        cf.select(
                            kid.sequence["sample"],
                            [],
                            size="xs",
                            leftSection=DashIconify(icon="mingcute:document-fill"),
                            className="kmviz-sample-select"
                        ),
                        cf.action(kid.sequence["download-button"], DashIconify(icon="bi:filetype-json", width=20), variant="filled", color=km_color),
                        dcc.Download(id=kid.sequence["download"])
                    )
                ),
                cf.tabs_panel(kid.sequence["graph-view-panel"], self._graph.layout(), value="graph"),
                cf.tabs_panel(kid.sequence["text-view-panel"], self._text.layout(), value="text"),
                value = "graph"
        )

    def callbacks(self) -> None:
        self._text.callbacks()
        self._graph.callbacks()

        @callback(
            Input(kid.kmviz("database"), "value"),
            Input(kid.kmviz("query"), "value"),
            State(kid.store["results"], "data"),
            Output(kid.sequence["sample"], "data"),
            Output(kid.sequence["sample"], "value"),
            prevent_initial_call=True
        )
        def update_sequence_data(db, query, results):
            if not db or not query or db.startswith("__kmviz_df"):
                prevent_update_on_none(None)

            qr = results[query][db]
            ids = list(qr.df["ID"])
            if not ids:
                return [], None
            return make_select_data(ids), ids[0]

        @callback(
            Input(kid.sequence["download-button"], "n_clicks"),
            State(kid.kmviz("database"), "value"),
            State(kid.kmviz("query"), "value"),
            State(kid.store["results"], "data"),
            Output(kid.sequence["download"], "data"),
            prevent_initial_call=True
        )
        def download_json(n_clicks, db, query, results):
            if n_clicks:
                if not db or not query or db.startswith("__kmviz_df"):
                    raise PreventUpdate

                qr = results[query][db]

                res={query: {}}

                for sample, response in qr.response.items():
                    if response.has_abs():
                        res[query][sample] = {"ykmer": response.covyk, "ybase": response.covyb}
                    else:
                        res[query][sample] = {"xkmer": response.covxk, "xbase": response.covxb}

                return dict(content=str(res), filename=f"{db}-{query}.json")
            return no_update


