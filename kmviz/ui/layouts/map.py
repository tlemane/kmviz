from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, ctx, callback
import dash_mantine_components as dmc
import dash
import pandas as pd
from dash import Patch
from dash_iconify import DashIconify
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import numpy as np
from pandas.api.types import is_numeric_dtype
import json

from kmviz.ui import state
from kmviz.ui.utils import prevent_update_on_none, make_select_data
from kmviz.ui.components.select import kgsf
from kmviz.ui.components.store import ksf
from kmviz.ui.components.figure import make_accordion, make_accordion_items
from kmviz.ui.components.figure import make_plot_title, make_plot_title_callbacks
from kmviz.ui.components.figure import make_plot_legend, make_plot_legend_callbacks
from kmviz.ui.components.figure import apply_presets, make_select_input, icons, make_nb_input
from kmviz.ui.components.figure import make_plot_shape, make_plot_shape_callbacks
from kmviz.ui.components.figure import make_color_legend, make_color_legend_callbacks
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

    data_panel = dmc.TabsPanel(value="data", children = [
        dmc.Group([
            make_select_input(
                kmap("color"), "Color", clearable=True, icon=icons("single")
            ),
            make_select_input(
                kmap("size"), "Size", clearable=True, icon=icons("single")
            ),
            make_select_input(
                kmap("text"), "Text", clearable=True, icon=icons("single")
            ),
            make_select_input(
                kmap("symbol"), "Symbol", clearable=True, icon=icons("single")
            ),
        ])
    ])

    anim_panel = dmc.TabsPanel(value="anim", children = [
        dmc.Group([
            make_select_input(
                kmap("animation_frame"), "Frame", clearable=True, icon=icons("single")
            ),
            make_select_input(
                kmap("animation_group"), "Group", clearable=True, icon=icons("single")
            )
        ])

    ])

    style_panel = dmc.TabsPanel(value="style", children = [
        dmc.Group([
            dmc.Select(
                id=kmap("template"),
                label="Theme",
                data=make_select_data(list(pio.templates)),
                clearable=True,
                searchable=True,
                value="seaborn",
                icon=icons("style")
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
                searchable=True,
                icon=icons("map")
            ),
            make_select_input(
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
                searchable=True,
                icon=icons("picker")
            ),
            make_select_input(
                id=kmap("color_div_continuous_scale"),
                label="Color diverging scale",
                data=make_select_data(
                    ['Portland', 'Picnic', 'Earth', 'Tropic', 'Tealrose', 'Temps', 'Geyser',
                     'Fall', 'Armyrose', 'oxy', 'curl', 'delta', 'balance',
                     'Spectral', 'RdYlGn', 'RdYlBu', 'RdGy', 'RdBu', 'PuOr', 'PiYG',
                     'PRGn', 'BrBG']

                ),
                clearable=True,
                searchable=True,
                icon=icons("picker")
            ),
            make_select_input(
                id=kmap("color_cyc_continuous_scale"),
                label="Color cyclical scale",
                data=make_select_data(
                    ['mygbm', 'mrybm', 'HSV', 'Phase', 'Edge', 'IceFire', 'Twilight']
                ),
                clearable=True,
                searchable=True,
                icon=icons("picker"),
            ),

            make_nb_input(
                kmap("color_continuous_midpoint"),
                "Color midpoint",
                (None, None, None, None),
                icon=icons("floating")
            ),
            make_nb_input(
                kmap("opacity"),
                "Opacity",
                (0.0, 0.01, 1.0, 0.7),
                2,
                icon=icons("floating")
            ),
            make_nb_input(
                kmap("size_max"),
                "Max size",
                (0, 1, 50, 15),
                icon=icons("integer"),
            ),
        ]),

        dmc.Group([
            dmc.JsonInput(
                id=kmap("color_discrete_map"),
                placeholder='ex: {"v1": "blue", "v2": "red"}',
                label="Color map",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json",
                icon=icons("json")
            ),
            dmc.JsonInput(
                id=kmap("symbol_map"),
                placeholder='ex: {"v1": "circle-open", "v2": "square-open"}',
                label="Symbol map",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json",
                icon=icons("json")
            ),
            dmc.JsonInput(
                id=kmap("color_discrete_sequence"),
                placeholder='ex: {"seq": ["red", "blue"] }',
                label="Color sequence",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json",
                icon=icons("json")
            ),
            dmc.JsonInput(
                id=kmap("symbol_sequence"),
                placeholder='ex: {"seq": ["circle-open", "square-open"] }',
                label="Symbol sequence",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json",
                icon=icons("json")
            ),
        ], grow=True)
    ])

    map_tab = dmc.Tabs([
        dmc.TabsList([
            dmc.Tab("Data", value="data"),
            dmc.Tab("Animation", value="anim"),
            dmc.Tab("Style", value="style"),
            dmc.Tab("Shape", value="shape"),
        ]),
        data_panel,
        anim_panel,
        style_panel,
        dmc.TabsPanel(make_plot_shape(kmap.child("shape")), value="shape")
    ], value = "data")

    preset_select = make_select_input(
        kmap.sid("select-preset"),
        None,
        placeholder="Select preset",
        clearable=True,
        icon=icons("preset"),
        style={"width": "170px"}
    )

    res =  html.Div([
        dcc.Graph(figure=blank_map(),
                  id=kmap.sid("figure"),
                  responsive=True,
                  mathjax=True,
                  style = { "margin-left": "auto",
                            "margin-right": "auto",
                            "height": "65vh",
                            "width":"95%" },
                  config = {'modeBarButtonsToAdd':['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]}
        ),
        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab("Map", value="map-MAP"),
                dmc.Tab("Title", value="map-TITLE"),
                dmc.Tab("Legend", value="map-LEGEND"),
                dmc.Tab("Colorbar", value="map-COLORBAR"),
                preset_select,
                dmc.ActionIcon(
                    DashIconify(icon="lucide:filter-x", width=20),
                    id=kmap.sid("rmf"),
                    variant="filled",
                    style = {"margin-left": "auto", "margin-right": 0},
                    color = "#1C7ED6"
                ),
            ]),
            dmc.TabsPanel(map_tab, value="map-MAP"),
            dmc.TabsPanel(make_plot_title(kmap.child("title")), value="map-TITLE"),
            dmc.TabsPanel(make_plot_legend(kmap.child("legend")), value="map-LEGEND"),
            dmc.TabsPanel(make_color_legend(kmap.child("colorbar")), value="map-COLORBAR")
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
        Input(kmap.sid("rmf"), "n_clicks"),
        Output(ktable.sid("grid"), "filterModel")
    )
    def remove_table_filters(n_clicks):
        if n_clicks:
            return {}
        prevent_update_on_none(None)

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
        State(kf.sid("plot-only"), "data"),
        prevent_initial_callbacks=True,
        prevent_initial_call=True
    )
    def update_map(data, template, color, size, text, symbol, aframe, agroup,
                   projection, cscs, cdcs, cccs, ccm, smap, sseq, cdm, cds, opacity,
                   size_max, preset_name, provider, session, plot_only):
        trigger = ctx.triggered_id
        args = ctx.args_grouping


        kmv_debug(f"{session}: 'update_map' triggered by '{trigger}'")

        if plot_only and "geodata" not in plot_only:
            return None, True

        if not data:
            return blank_map(), True

        df = pd.DataFrame.from_dict(data)

        scales = [cscs, cdcs, cccs]
        scale=None
        if any(scales):
            scale = next(s for s in scales if s is not None)

        if "geodata" in plot_only:
            geo = plot_only["geodata"]
        else:
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
        Input(ktable.sid("grid"), "virtualRowData"),
        Output(kmap("color"), "data"),
        Output(kmap("size"), "data"),
        Output(kmap("text"), "data"),
        Output(kmap("symbol"), "data"),
        Output(kmap("animation_frame"), "data"),
        Output(kmap("animation_group"), "data"),
        prevent_initial_callbacks=True,
        prevent_initial_call=True
    )
    def init_map_selectors(data):

        df = pd.DataFrame.from_dict(data)
        cols = make_select_data(list(df))

        cols_size = []
        for c in list(df):
            if is_numeric_dtype(df[c]):
                if all(x >= 0 for x in df[c]):
                    cols_size.append(c)


        return cols, cols_size, cols, cols, cols, cols


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

    if not state.kmstate.plot_only:
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

    make_plot_legend_callbacks(kmap.child("legend"), kmap.sid("figure"))
    make_plot_title_callbacks(kmap.child("title"), kmap.sid("figure"))
    make_plot_shape_callbacks(kmap.child("shape"), kmap.sid("figure"))
    make_color_legend_callbacks(kmap.child("colorbar"), kmap.sid("figure"))
