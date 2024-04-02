from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, ctx, callback
import dash_mantine_components as dmc
import dash
import pandas as pd
from dash import Patch

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from pandas.api.types import is_numeric_dtype
import json

from kmviz.ui import state
from kmviz.ui.utils import prevent_update_on_none, make_select_data
from kmviz.ui.components.select import kgsf
from kmviz.ui.components.store import ksf
from kmviz.ui.components.figure import make_accordion, make_accordion_items
from kmviz.ui.components.figure import make_plot_title, make_plot_title_callbacks
from kmviz.ui.components.figure import make_plot_legend, make_plot_legend_callbacks
from kmviz.ui.components.figure import apply_presets
from kmviz.ui.layouts.table import ktable
from kmviz.ui.layouts.sequence import kseq
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.core.log import kmv_debug

kmap = kf.child("map")

def blank_map():
    fig = go.Figure(go.Scattergeo())
    fig.update_layout(template = "seaborn")
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig

def make_map_layout():

    map_tab = make_accordion([
      make_accordion_items("Data", [
            dmc.Group([
                dmc.Select(id=kmap("color"), label="Color", clearable=True),
                dmc.Select(id=kmap("size"), label="Size", clearable=True),
                dmc.Select(id=kmap("text"), label="Text", clearable=True),
                dmc.Select(id=kmap("symbol"), label="Symbol", clearable=True),
            ])
        ]),
        make_accordion_items("Animation", [
            dmc.Group([
                dmc.Select(id=kmap("animation_frame"), label="Frame", clearable=True),
                dmc.Select(id=kmap("animation_group"), label="Group", clearable=True)
            ])
        ]),
        make_plot_title(kmap.child("title")),
        make_accordion_items("Style", [
            dmc.Group([
                dmc.Select(
                    id=kmap("template"),
                    label="Theme",
                    data=make_select_data(list(pio.templates)),
                    clearable=True,
                    searchable=True,
                    value="seaborn"
                ),
                dmc.Select(
                    id=kmap("projection"),
                    label="Projection",
                    data=make_select_data([
                        'equirectangular', 'mercator', 'orthographic', 'natural earth',
                        'kavrayskiy7', 'miller', 'robinson', 'eckert4', 'azimuthal equal area',
                        'azimuthal equidistant', 'conic equal area', 'conic conformal',
                        'conic equidistant', 'gnomonic', 'stereographic', 'mollweide', 'hammer',
                        'transverse mercator', 'albers usa', 'winkel tripel', 'aitoff', 'sinusoidal'
                    ]),
                    value="equirectangular",
                    clearable=True,
                    searchable=True
                ),
                dmc.NumberInput(
                    id=kmap("opacity"),
                    label="Opacity",
                    value=0.7,
                    precision=2,
                    min=0.0,
                    max=1.0,
                    step=0.05
                ),
            ]),
            dmc.Group([
                dmc.Select(
                    id=kmap("color_seq_continuous_scale"),
                    label="Color sequential scale",
                    data=make_select_data(
                         ['Brwnyl', 'Agsunset', 'Sunsetdark', 'Magenta', 'Sunset',
                         'Purpor', 'Purp', 'Tealgrn', 'Teal', 'Bluyl', 'Aggrnyl',
                         'Emrld', 'Darkmint', 'Blugrn', 'Mint', 'Pinkyl',
                         'Peach', 'Oryel', 'Redor', 'Burgyl', 'Burg',
                         'tempo', 'amp', 'speed', 'matter', 'algae', 'dense', 'deep',
                         'gray', 'ice', 'solar', 'haline', 'thermal', 'turbid', 'YlOrRd',
                         'YlOrBr', 'YlGnBu', 'YlGn', 'Reds', 'RdPu', 'RdBu', 'Purples',
                         'PuRd', 'PuBuGn', 'PuBu', 'Oranges', 'OrRd', 'Greys', 'Greens',
                         'GnBu', 'BuPu', 'BuGn', 'Blues', 'Rainbow', 'Jet', 'Hot', 'Electric',
                         'Bluered', 'Blackbody', 'Turbo', 'Plasma', 'Magma', 'Inferno',
                         'Cividis', 'Viridis', 'Plotly3']
                    ),
                    clearable=True,
                    searchable=True
                ),
                dmc.Select(
                    id=kmap("color_div_continuous_scale"),
                    label="Color diverging scale",
                    data=make_select_data(
                        ['Portland', 'Picnic', 'Earth', 'Tropic', 'Tealrose', 'Temps', 'Geyser',
                         'Fall', 'Armyrose', 'oxy', 'curl', 'delta', 'balance',
                         'Spectral', 'RdYlGn', 'RdYlBu', 'RdGy', 'RdBu', 'PuOr', 'PiYG',
                         'PRGn', 'BrBG']

                    ),
                    clearable=True,
                    searchable=True
                ),
                dmc.Select(
                    id=kmap("color_cyc_continuous_scale"),
                    label="Color cyclical scale",
                    data=make_select_data(
                        ['mygbm', 'mrybm', 'HSV', 'Phase', 'Edge', 'IceFire', 'Twilight']
                    ),
                    clearable=True,
                    searchable=True
                ),
                dmc.NumberInput(
                    id=kmap("color_continuous_midpoint"),
                    label="Color midpoint",
                    value=None
                ),
                dmc.NumberInput(
                    id=kmap("size_max"),
                    label="Max size",
                    min=0, step=1, value=20
                ),
            ]),
            dmc.JsonInput(
                id=kmap("color_discrete_map"),
                placeholder="ex: {'value1': 'blue', 'value2': 'red'}",
                label="Color map (json)",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json"
            ),
            dmc.JsonInput(
                id=kmap("symbol_map"),
                placeholder="ex: {'value1': 'circle-open', 'value2': 'square-open'}",
                label="Symbol map (json)",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json"
            ),
            dmc.JsonInput(
                id=kmap("color_discrete_sequence"),
                placeholder="ex: {'seq': ['red', 'blue'] }",
                label="Color sequence (json)",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json"
            ),
            dmc.JsonInput(
                id=kmap("symbol_sequence"),
                placeholder="ex: {'seq': ['circle-open', 'square-open'] }",
                label="Symbol sequence (json)",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json"
            ),

        ]),
    ])

    res =  html.Div([
        dmc.Space(h=5),

        html.Div([
            dmc.Group([
                dmc.Select(
                    id=kmap.sid("select-preset"),
                    placeholder="Select preset",
                    clearable=True
                ),
            ])
        ], id=kmap.sid("presets-div")),

        dcc.Graph(figure=blank_map(),
                  id=kmap.sid("figure"),
                  responsive=True,
                  mathjax=True,
                  style = { "margin-left": "auto",
                            "margin-right": "auto",
                            "height": "65vh",
                            "width":"95%" }
        ),
        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab("Map", value="map-MAP"),
                dmc.Tab("Legend", value="map-LEGEND"),
            ]),
            dmc.TabsPanel(map_tab, value="map-MAP"),
            dmc.TabsPanel(make_plot_legend(kmap.child("legend")), value="map-LEGEND")
        ], value="map-MAP")

    ], id="map-panel", style = {"height":"100%", "width":"100%"})

    return res

def from_json(value, p=None):
    try:
        value = json.loads(value)
        if p:
            value = value[p]
        return value
    except:
        return None

def make_map_layout_callbacks():

    @callback(
        Output(kmap.sid("figure"), "figure"),
        Output(kmap.sid("panel"), "disabled"),
        Input(ktable.sid("grid"), "virtualRowData"),
        Input(kmap("template"), "value"),
        Input(kmap("color"), "value"),
        Input(kmap("size"), "value"),
        Input(kmap("text"), "value"),
        Input(kmap("symbol"), "value"),
        Input(kmap("animation_frame"), "value"),
        Input(kmap("animation_group"), "value"),
        Input(kmap("projection"), "value"),
        Input(kmap("color_seq_continuous_scale"), "value"),
        Input(kmap("color_div_continuous_scale"), "value"),
        Input(kmap("color_cyc_continuous_scale"), "value"),
        Input(kmap("color_continuous_midpoint"), "value"),
        Input(kmap("symbol_map"), "value"),
        Input(kmap("symbol_sequence"), "value"),
        Input(kmap("color_discrete_map"), "value"),
        Input(kmap("color_discrete_sequence"), "value"),
        Input(kmap("opacity"), "value"),
        Input(kmap("size_max"), "value"),
        Input(kmap.sid("select-preset"), "value"),
        State(kgsf("provider"), "value"),
        State(kf.sid("session-id"), "data"),
        prevent_initial_callbacks=True,
        prevent_initial_call=True
    )
    def update_map(data, template, color, size, text, symbol, aframe, agroup,
                   projection, cscs, cdcs, cccs, ccm, smap, sseq, cdm, cds, opacity,
                   size_max, preset_name, provider, session):
        trigger = ctx.triggered_id
        args = ctx.args_grouping

        kmv_debug(f"{session}: 'update_map' triggered by '{trigger}'")

        if not data:
            return blank_map(), True

        df = pd.DataFrame.from_dict(data)

        scales = [cscs, cdcs, cccs]
        scale=None
        if any(scales):
            scale = next(s for s in scales if s is not None)

        geo = state.kmstate.providers.get(provider).db.geodata

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

        if preset_name:
            presets = state.kmstate.providers.get(provider).presets["map"][preset_name].copy()
            priority = presets["priority"]
            del presets["priority"]
            del presets["name"]
            params = apply_presets(presets, params, priority)

        return px.scatter_geo(df, hover_name="ID", **params), False

    @callback(
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kmap("color"), "data"),
        Output(kmap("size"), "data"),
        Output(kmap("text"), "data"),
        Output(kmap("symbol"), "data"),
        Output(kmap("animation_frame"), "data"),
        Output(kmap("animation_group"), "data"),
        prevent_initial_callbacks=True,
        prevent_initial_call=True
    )
    def init_map_selectors(provider, query, qr):
        prevent_update_on_none(provider)

        df = qr[query][provider].df
        cols = make_select_data(list(df))

        cols_size = []
        for c in list(df):
            if is_numeric_dtype(df[c]):
                if all(x > 0 for x in df[c]):
                    cols_size.append(c)

        return cols, cols_size, cols, cols, cols, cols

    @callback(
        Input(kmap.sid("figure"), "clickData"),
        Output(kseq.sid("select"), "value"),
        Output(ktable.sid("grid"), "filterModel"),
        Output("tab-select", "value"),
        prevent_initial_callbacks=True,
    )
    def on_click_data_map(value):
        sample = value["points"][0]["hovertext"]

        p = Patch()
        p["ID"] = {'filterType': 'text', 'type': 'equals', 'filter': sample}

        return sample, p, "sequence"

    @callback(
        Input(kmap.sid("figure"), "selectedData"),
        State(ksf("query-results"), "data"),
        Output(ktable.sid("grid"), "filterModel"),
        prevent_initial_callbacks=True
    )
    def on_selected(sdata, query):
        trigger = ctx.triggered_id

        if trigger == kmap.sid("figure"):
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

        raise dash.exceptions.PreventUpdate()

    make_plot_legend_callbacks(kmap.child("legend"), kmap.sid("figure"))
    make_plot_title_callbacks(kmap.child("title"), kmap.sid("figure"))
