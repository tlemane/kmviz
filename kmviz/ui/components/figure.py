from dash_extensions.enrich import Input, Output, State, html, ctx, callback, dcc
from dash import Patch, no_update
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash_iconify import DashIconify
from kmviz.ui.utils import make_select_data, prevent_update_on_none, prevent_update_on_empty
from kmviz.ui.patch import patch_value, patch_value_id

import plotly.graph_objects as go
import json

import plotly.io as pio
import numpy as np
import plotly.express as px


def make_accordion_items(name: str, children: list):
    return dmc.AccordionItem([
        dmc.AccordionControl(name),
        dmc.AccordionPanel(children=children)
    ], value=name)

def make_accordion(children: list):
    return dmc.AccordionMultiple(
        children=children,
    )


def make_on_off_radio(id: str, label: str):
    return dmc.RadioGroup(
        [dmc.Radio("On", value="True"), dmc.Radio("Off", value="False")],
        id=id,
        label=label
    )

def make_hover_color_picker(id: str,
                            label: str="",
                            color: str=dict(rgb=dict(r=0,g=0,b=0,a=0.9))):
    target = f"{id['type']}-{id['index']}-pop"
    return html.Div([
        DashIconify(id=target, icon="noto:artist-palette", width=30, style = {"margin":"auto"}),
        dbc.Popover(
            daq.ColorPicker(
                id=id,
                label=label,
                value=color,
                size=200,
                className="daq-fixed-cp"
            ),
            trigger="hover",
            target=target,
        )
    ])

def from_json(value, p=None):
    try:
        value = json.loads(value)
        if p:
            value = value[p]
        return value
    except:
        return None

def color_to_string(c):
    if "rgb" in c:
        m = c["rgb"]
        return f"rgba({m['r']},{m['g']},{m['b']},{m['a']})"
    elif "hex" in c:
        return c["hex"]
    return c

def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)

def fix_none_on_fig_data(inputs):
    # fix: https://github.com/plotly/plotly.js/issues/6310
    if "xaxis" in inputs[0]["layout"] and "rangeslider" in inputs[0]["layout"]["xaxis"]:
        if "yaxis" in inputs[0]["layout"]["xaxis"]["rangeslider"]:
            del inputs[0]["layout"]["xaxis"]["rangeslider"]["yaxis"]

    if "xaxis" in inputs[0]["layout"] and "rangeslider" in inputs[0]["layout"]["xaxis"]:
        if "yaxis2" in inputs[0]["layout"]["xaxis"]["rangeslider"]:
            del inputs[0]["layout"]["xaxis"]["rangeslider"]["yaxis2"]


    # fix: https://github.com/plotly/plotly.py/issues/4280
    for x in range(len(inputs[0]["data"])):
        if "marker" in inputs[0]["data"][x] and "color" in inputs[0]["data"][x]["marker"]:
            for i in range(len(inputs[0]["data"][x]["marker"]["color"])):
                if inputs[0]["data"][x]["marker"]["color"][i] is None:
                   inputs[0]["data"][x]["marker"]["color"][i] = np.nan

    for x in item_generator(inputs[0], "rangeslider"):
        if "yaxis2" in x:
            del x["yaxis2"]

def patch_figure(context, paths = ["layout"]):
    args = context.args_grouping
    trigger = context.triggered_id

    for e in args["inputs"]:
        if e["id"] == trigger:
            if isinstance(e["value"], dict):
                e["value"] = color_to_string(e["value"])
            return patch_value_id(Patch(paths), trigger, e["value"])

    return no_update

def apply_presets(presets: dict, params: dict, priority: True):
    if not presets:
        return params

    if priority:
        return {**params, **presets}
    else:
        for k, v in params.items():
            if k in presets and v is not None:
                presets[k] = v
        return {**params, **presets}


        return {**presets, **params}
def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = "seaborn")
    return fig

def list_to_str(value):
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value

def make_plot_px(ptype: str, df, X, Y, Z=None, params={}):
    X, Y, Z = list_to_str(X), list_to_str(Y), list_to_str(Z)

    if ptype == "Bar":
        return px.bar(df, x=X, y=Y, hover_name="ID", **params)

    if ptype == "Line":
        return px.line(df, x=X, y=Y, hover_name="ID", **params)

    if ptype == "Area":
        return px.area(df, x=X, y=Y, hover_name="ID", **params)

    if ptype == "Scatter":
        return px.scatter(df, x=X, y=Y, hover_name="ID", **params)

    if ptype == "Scatter3D":
        return px.scatter_3d(df, x=X, y=Y, z=Z, hover_name="ID", **params)

    if ptype == "Pie":
        return px.pie(df, hover_name="ID", **params),

    if ptype == "Parallel coordinates":
        prevent_update_on_empty(params["dimensions"])
        return px.parallel_coordinates(df, **params)

    if ptype == "Parallel categories":
        prevent_update_on_empty(params["dimensions"])
        return px.parallel_categories(df, **params)

    if ptype == "Scatter matrix":
        prevent_update_on_empty(params["dimensions"])
        return px.scatter_matrix(df, **params, hover_name="ID")

    if ptype == "Density contour":
        ct = None
        if "contours_coloring" in params:
            ct = params["contours_coloring"]
            del params["contours_coloring"]
        fig = px.density_contour(df, x=X, y=Y, z=Z, hover_name="ID", **params)

        if ct:
            fig.update_traces(contours_coloring=ct)

        return fig

    if ptype == "Density heatmap":
        return px.density_heatmap(df, x=X, y=Y, z=Z, hover_name="ID", **params)

    if ptype == "Violin":
        return px.violin(df, x=X, y=Y, hover_name="ID", **params)

    if ptype == "Box":
        return px.box(df, x=X, y=Y, hover_name="ID", **params)


px_bar_options = {
    "type",
    "xselect",
    "yselect",
    "color",
    "pattern_shape",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "hover_name",
    "hover_data",
    "custom_data",
    "text",
    "base",
    "error_x",
    "error_x_minus",
    "error_y",
    "error_y_minus",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "color_discrete_sequence",
    "color_discrete_map",
    "color_continuous_scale",
    "pattern_shape_sequence",
    "pattern_shape_map",
    "range_color",
    "color_continuous_midpoint",
    "opacity",
    "orientation",
    "barmode",
    "log_x",
    "log_y",
    "range_x",
    "range_y",
    "text_auto",
    "title",
    "template",
    "width",
    "height",
    "color_seq_continuous_scale",
    "color_div_continuous_scale",
    "color_cyc_continuous_scale",
}

px_scatter_options = {
    "type",
    "xselect",
    "yselect",
    "size",
    "color",
    "text",
    "symbol",
    "animation_frame",
    "animation_group",
    "color_continuous_midpoint",
    "color_continuous_scale",
    "symbol_map",
    "symbol_sequence",
    "color_discrete_map",
    "color_discrete_sequence",
    "opacity",
    "size_max",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "template",
    "marginal_x",
    "marginal_y",
    "trendline",
    "trendline_scope",
    "trendline_options",
    "color_seq_continuous_scale",
    "color_div_continuous_scale",
    "color_cyc_continuous_scale",
}

px_line_options = {
    "type",
    "xselect",
    "yselect",
    "line_group",
    "color",
    "line_dash",
    "symbol",
    "hover_name",
    "hover_data",
    "custom_data",
    "text",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "error_x",
    "error_x_minus",
    "error_y",
    "error_y_minus",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "orientation",
    "color_discrete_sequence",
    "color_discrete_map",
    "line_dash_sequence",
    "line_dash_map",
    "symbol_sequence",
    "symbol_map",
    "markers",
    "log_x=",
    "log_y=",
    "range_x",
    "range_y",
    "line_shape",
    "render_mode",
    "title",
    "template",
    "width",
    "height"
}

px_area_options = {
    "type",
    "xselect",
    "yselect",
    "line_group",
    "color",
    "symbol",
    "hover_name",
    "hover_data",
    "custom_data",
    "text",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "error_x",
    "error_x_minus",
    "error_y",
    "error_y_minus",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "orientation",
    "color_discrete_sequence",
    "color_discrete_map",
    "symbol_sequence",
    "symbol_map",
    "markers",
    "log_x=",
    "log_y=",
    "range_x",
    "range_y",
    "line_shape",
    "render_mode",
    "title",
    "template",
    "width",
    "height"
}
px_scatter3d_options = {
    "type",
    "xselect",
    "yselect",
    "zselect",
}

px_pcoord_options = {
    "type",
    "dimensions",
    "color",
    "labels",
    "color_continuous_scale",
    "range_color",
    "color_continuous_midpoint",
    "title",
    "template",
    "width",
    "height",
    "color_seq_continuous_scale",
    "color_div_continuous_scale",
    "color_cyc_continuous_scale",

}

px_pcat_options = {
    "type",
    "dimensions",
    "color",
    "labels",
    "color_continuous_scale",
    "range_color",
    "color_continuous_midpoint",
    "title",
    "template",
    "width",
    "height",
    "dimensions_max_cardinality",
    "color_seq_continuous_scale",
    "color_div_continuous_scale",
    "color_cyc_continuous_scale",

}

px_pie_options = {
    "type",
    "names",
    "values",
    "color",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "color_discrete_sequence",
    "color_discrete_map",
    "hover_name",
    "hover_data",
    "custom_data",
    "category_orders",
    "labels",
    "title",
    "template",
    "width",
    "height",
    "opacity",
    "hole"
}

px_matrix_options = {
    "type",
    "dimensions",
    "color",
    "symbol",
    "size",
    "hover_name",
    "hover_data",
    "custom_data",
    "category_orders",
    "labels",
    "color_discrete_sequence",
    "color_discrete_map",
    "color_continuous_scale",
    "range_color",
    "color_continuous_midpoint",
    "symbol_sequence",
    "symbol_map",
    "opacity",
    "size_max",
    "title",
    "template",
    "width",
    "height",
    "color_seq_continuous_scale",
    "color_div_continuous_scale",
    "color_cyc_continuous_scale",

}

px_density_heat = {
    "xselect",
    "yselect",
    "zselect",
    "type",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "hover_name",
    "hover_data",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "orientation",
    "color_continuous_scale",
    "range_color",
    "color_continuous_midpoint",
    "marginal_x",
    "marginal_y",
    "log_x",
    "log_y",
    "range_x",
    "range_y",
    "histfunc",
    "histnorm",
    "nbinsx",
    "nbinsy",
    "text_auto",
    "title",
    "template",
    "width",
    "height",
    "color_seq_continuous_scale",
    "color_div_continuous_scale",
    "color_cyc_continuous_scale",

}

px_density_contour = {
    "xselect",
    "yselect",
    "zselect",
    "type",
    "color",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "hover_name",
    "hover_data",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "orientation",
    "color_discrete_sequence",
    "color_discrete_map",
    "marginal_x",
    "marginal_y",
    "trendline",
    "trendline_options",
    "trendline_color_override",
    "trendline_scope",
    "log_x",
    "log_y",
    "range_x",
    "range_y",
    "histfunc",
    "histnorm",
    "nbinsx",
    "nbinsy",
    "text_auto",
    "title",
    "template",
    "width",
    "contours_coloring",
    "height"
}

px_violin_options = {
    "xselect",
    "yselect",
    "type",
    "color",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "hover_name",
    "hover_data",
    "custom_data",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "color_discrete_sequence",
    "color_discrete_map",
    "orientation",
    "violinmode",
    "log_x",
    "log_y",
    "range_x",
    "range_y",
    "points",
    "box",
    "title",
    "template",
    "width",
    "height"
}

px_box_options = {
    "xselect",
    "yselect",
    "type",
    "color",
    "facet_row",
    "facet_col",
    "facet_col_wrap",
    "facet_row_spacing",
    "facet_col_spacing",
    "hover_name",
    "hover_data",
    "custom_data",
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "color_discrete_sequence",
    "color_discrete_map",
    "orientation",
    "boxmode",
    "log_x",
    "log_y",
    "range_x",
    "range_y",
    "points",
    "notched",
    "title",
    "template",
    "width",
    "height"
}

px_options = {
    "Bar": px_bar_options,
    "Scatter": px_scatter_options,
    "Line": px_line_options,
    "Area": px_area_options,
    "Scatter3D": px_scatter3d_options,
    "Pie": px_pie_options,
    "Parallel coordinates": px_pcoord_options,
    "Parallel categories": px_pcat_options,
    "Scatter matrix": px_matrix_options,
    "Density heatmap": px_density_heat,
    "Density contour": px_density_contour,
    "Violin": px_violin_options,
    "Box": px_box_options
}


def fix_px_params(params, ptype):
    for k in list(params):
        if k not in px_options[ptype]:
            del params[k]
    return params

def make_plot_title(factory):

    pid = factory
    return make_accordion([
        make_accordion_items("Title", [
            dmc.TextInput(id=pid("title_text"), label="Title", debounce=0.5, value="<b>Title</b>"),
            dmc.Group([
                dmc.NumberInput(label="Size", id=pid("title_font_size"), min=1, step=1, max=60, value=16),
                dmc.Select(
                    id=pid("title_font_family"),
                    label="Font",
                    data=make_select_data([
                        "Arial", "Balto", "Courier New", "Droid Sans",
                        "Droid Serif", "Droid Sans Mono", "Gravitas One",
                        "Old Standard TT", "Open Sans", "Overpass",
                        "PT Sans Narrow", "Raleway", "Times New Roman"
                    ]),
                    value="Arial"
                ),
                make_hover_color_picker(pid("title_font_color"), "", dict(hex="#000000")),
            ]),
            dmc.Group([
                dmc.Select(
                    id=pid("title_xanchor"),
                    label="Anchor X",
                    data=make_select_data(["auto", "left", "center", "right"]),
                    value="center"
                ),
                dmc.Select(
                    id=pid("title_xref"),
                    label="Ref X",
                    data=make_select_data(["container", "paper"]),
                    value="container",
                ),
                dmc.NumberInput(label="x", id=pid("title_x"), min=0.0, precision=2, max=1.0, step=0.01, value=0.5)
            ]),
            dmc.Group([
                dmc.Select(
                    id=pid("title_yanchor"),
                    label="Anchor Y",
                    data=make_select_data(["auto", "top", "middle", "bottom"]),
                    value="top"
                ),
                dmc.Select(
                    id=pid("title_yref"),
                    label="Ref Y",
                    data=make_select_data(["container", "paper"]),
                    value="container"
                ),
                dmc.NumberInput(label="y", id=pid("title_y"), min=0.0, precision=2, max=1.0, step=0.01, value=0.95)
            ]),
        ])
    ])


def make_plot_title_callbacks(factory, figure_id):
    pid = factory

    @callback(
        Output(figure_id, "figure", allow_duplicate=True),
        inputs=dict(inputs=(
            Input(pid("title_text"), "value"),
            Input(pid("title_font_size"), "value"),
            Input(pid("title_font_family"), "value"),
            Input(pid("title_font_color"), "value"),
            Input(pid("title_xanchor"), "value"),
            Input(pid("title_xref"), "value"),
            Input(pid("title_x"), "value"),
            Input(pid("title_yanchor"), "value"),
            Input(pid("title_yref"), "value"),
            Input(pid("title_y"), "value"),
        )),
        prevent_initial_callbacks=True
    )
    def update_title(inputs):
        return patch_figure(ctx)

def make_plot_legend(factory):
    pid = factory

    res = html.Div([
        dmc.Switch(id=pid("showlegend"), label="Show", checked=True),
        make_accordion([
            make_accordion_items(f"Title", [
                dmc.Group([
                    dmc.TextInput(label="Text", id=pid("legend_title_text")),
                    make_hover_color_picker(pid("legend_title_font_color"), "", dict(hex="#000000"))
                ]),
                dmc.Group([
                    dmc.NumberInput(label="Size", id=pid("legend_title_font_size"), min=0, step=1, value=13),
                    dmc.Select(
                        id=pid("legend_title_font_family"),
                        label="Font",
                        data=make_select_data([
                            "Arial", "Balto", "Courier New", "Droid Sans",
                            "Droid Serif", "Droid Sans Mono", "Gravitas One",
                            "Old Standard TT", "Open Sans", "Overpass",
                            "PT Sans Narrow", "Raleway", "Times New Roman"
                        ]),
                        value="Arial"
                    ),
                    dmc.Select(
                        id=pid("legend_title_side"),
                        label="Position",
                        data=make_select_data(["top", "left", "top left", "top center", "top right"]),
                        value="top center"
                    )
                ]),
            ]),
            make_accordion_items(f"Entries", [
                dmc.Group([
                    dmc.NumberInput(label="Size", id=pid("legend_font_size"), min=0, step=1, value=10),
                    dmc.Select(
                        id=pid("legend_font_family"),
                        label="Font",
                        data=make_select_data([
                            "Arial", "Balto", "Courier New", "Droid Sans",
                            "Droid Serif", "Droid Sans Mono", "Gravitas One",
                            "Old Standard TT", "Open Sans", "Overpass",
                            "PT Sans Narrow", "Raleway", "Times New Roman"
                        ]),
                        value="Arial"
                    ),
                    make_hover_color_picker(pid("legend_font_color"), "", dict(hex="#000000"))
                ]),
            ]),
            make_accordion_items(f"Box", [
                dmc.Group([
                    dmc.NumberInput(label="Width", id=pid("legend_borderwidth"), value=0, min=0, step=1),
                    make_hover_color_picker(pid("legend_bordercolor"), "Border"),
                    make_hover_color_picker(pid("legend_bgcolor"), "Background"),
                ]),
            ]),
            make_accordion_items("Position", [
                dmc.NumberInput(label="Indentation", id=pid("legend_indentation"), min=-15, step=1, value=0),
                dmc.RadioGroup(
                    [dmc.Radio("vertical", value="v"), dmc.Radio("horizontal", value="h")],
                    id=pid("legend_orientation"),
                    label="Orientation",
                    value="v"
                ),
                dmc.Group([
                    dmc.Select(
                        id=pid("legend_xanchor"),
                        label="Anchor X",
                        data=make_select_data(["auto", "left", "center", "right"]),
                        value="right"
                    ),
                    dmc.Select(
                        id=pid("legend_xref"),
                        label="Ref X",
                        data=make_select_data(["container", "paper"]),
                        value="paper"
                    ),
                    dmc.NumberInput(label="x", id=pid("legend_x"), min=0.0, precision=2, max=1.0, step=0.01, value=0.9)
                ]),
                dmc.Group([
                    dmc.Select(
                        id=pid("legend_yanchor"),
                        label="Anchor Y",
                        data=make_select_data(["auto", "top", "middle", "bottom"]),
                        value="top"
                    ),
                    dmc.Select(
                        id=pid("legend_yref"),
                        label="Ref Y",
                        data=make_select_data(["container", "paper"]),
                        value="paper"
                    ),
                    dmc.NumberInput(label="y", id=pid("legend_y"), min=0.0, precision=2, max=1.0, step=0.01, value=1.0)
                ])
            ])
        ])
    ])

    return res

def make_plot_legend_callbacks(factory, figure_id):

    pid = factory

    @callback(
        Output(figure_id, "figure", allow_duplicate=True),
        inputs=dict(inputs=(
            Input(pid("showlegend"), "checked"),
            Input(pid("legend_title_text"), "value"),
            Input(pid("legend_title_font_size"), "value"),
            Input(pid("legend_title_font_family"), "value"),
            Input(pid("legend_title_font_color"), "value"),
            Input(pid("legend_title_side"), "value"),
            Input(pid("legend_font_size"), "value"),
            Input(pid("legend_font_family"), "value"),
            Input(pid("legend_font_color"), "value"),
            Input(pid("legend_borderwidth"), "value"),
            Input(pid("legend_bordercolor"), "value"),
            Input(pid("legend_bgcolor"), "value"),
            Input(pid("legend_indentation"), "value"),
            Input(pid("legend_orientation"), "value"),
            Input(pid("legend_orientation"), "value"),
            Input(pid("legend_xanchor"), "value"),
            Input(pid("legend_xref"), "value"),
            Input(pid("legend_x"), "value"),
            Input(pid("legend_yanchor"), "value"),
            Input(pid("legend_yref"), "value"),
            Input(pid("legend_y"), "value"),
        )),
        prevent_initial_call=True,
        prevent_initial_callbacks= True
    )
    def update_legend(inputs):
        return patch_figure(ctx)

def make_trace(factory):
    pid = factory

    res = html.Div([
         make_accordion([
            dmc.Group([
                dmc.Select(
                    id=pid("type") ,
                    label="Type",
                    data=make_select_data([
                        "Scatter",
                        "Line",
                        "Area",
                        "Bar",
                        "Scatter3D",
                        "Parallel categories",
                        "Parallel coordinates",
                        "Scatter matrix",
                        "Density heatmap",
                        "Density contour",
                        "Violin",
                        "Box"
                    ]),
                    required=True,
                    clearable=True,
                    searchable=True
                ),
            ]),
            make_accordion_items("Data", [
                dmc.Group([
                    dmc.MultiSelect(
                        id=pid("xselect"),
                        label="X",
                        value=[],
                    ),
                    dmc.MultiSelect(
                        id=pid("yselect"),
                        label="Y",
                        value=[]
                    ),
                    dmc.MultiSelect(
                        id=pid("zselect"),
                        label="Z",
                        value=[]
                    ),
                ]),
                dmc.Group([
                    dmc.Select(id=pid("color"), label="Color", clearable=True, searchable=True),
                    dmc.Select(id=pid("size"), label="Size", clearable=True, searchable=True),
                    dmc.Select(id=pid("text"), label="Text", clearable=True, searchable=True),
                    dmc.Select(id=pid("symbol"), label="Symbol", clearable=True, searchable=True),
                    dmc.Select(id=pid("pattern_shape"), label="Pattern shape", clearable=True, searchable=True),
                    dmc.Select(id=pid("base"), label="Base", clearable=True, searchable=True),
                    dmc.Select(id=pid("line_dash"), label="Line dash", clearable=True, searchable=True),
                    dmc.Select(id=pid("line_group"), label="Line group", clearable=True, searchable=True),
                    dmc.MultiSelect(id=pid("dimensions"), label="Dimensions", clearable=True, searchable=True),
                    dmc.Select(id=pid("values"), label="Values", clearable=True, searchable=True),
                    dmc.Select(id=pid("names"), label="Names", clearable=True, searchable=True),
                    dmc.Select(
                        id=pid("barmode"),
                        label="Bar mode",
                        clearable=True,
                        searchable=True,
                        data=make_select_data(["relative", "group", "overlay"])
                    ),
                    dmc.Select(
                        id=pid("line_shape"),
                        label="Line shape",
                        clearable=True,
                        searchable=True,
                        data=make_select_data(["hv", "vh", "hvh", "vhv", "spline", "linear"])
                    ),
                ])
            ]),
            make_accordion_items("Animation", [
                dmc.Group([
                    dmc.Select(id=pid("animation_frame"), label="Frame", clearable=True, searchable=True),
                    dmc.Select(id=pid("animation_group"), label="Group", clearable=True, searchable=True)
                ])
            ]),
            make_accordion_items("Distribution", [
                dmc.Group([
                    dmc.Select(
                        id=pid("violinmode"),
                        label="Violin mode",
                        value="group",
                        data=make_select_data([
                            "group", "overlay"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                    dmc.Select(
                        id=pid("boxmode"),
                        label="Box mode",
                        value="group",
                        data=make_select_data([
                            "group", "overlay"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                    dmc.Select(
                        id=pid("points"),
                        label="Points",
                        value="outliers",
                        data=make_select_data([
                            "outliers", "suspectedoutliers", "all", "False"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                    dmc.Select(
                        id=pid("box"),
                        label="Violin box",
                        value="False",
                        data=make_select_data([
                            "True", "False"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                    dmc.Select(
                        id=pid("notched"),
                        label="Box notches",
                        value="False",
                        data=make_select_data([
                            "True", "False"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                ])
            ]),
            make_accordion_items("Density", [
                dmc.Group([
                    dmc.Select(
                        id=pid("histfunc"),
                        label="Hist function",
                        value="count",
                        data=make_select_data([
                            "count", "sum", "avg", "min", "max"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                    dmc.Select(
                        id=pid("histnorm"),
                        label="Hist norm",
                        data=make_select_data([
                            "percent", "probability", "density", "probability density"
                        ]),
                        clearable=True,
                        searchable=True,
                    ),

                    dmc.NumberInput(
                        id=pid("nbinsx"),
                        label="X bins",
                        min=0,
                        value=4,
                        step=1
                    ),
                    dmc.NumberInput(
                        id=pid("nbinsy"),
                        label="Y bins",
                        min=0,
                        value=4,
                        step=1
                    ),
                    dmc.Select(
                        id=pid("contours_coloring"),
                        label="Contours coloring",
                        value="lines",
                        data=make_select_data([
                            "fill", "heatmap", "lines", "none",
                        ]),
                        clearable=True,
                        searchable=True,
                    ),
                ])
            ]),
            make_accordion_items("Facet", [
                dmc.Group([

                    dmc.Select(
                        id=pid("facet_row"),
                        label="Row",
                        clearable=True,
                    ),
                    dmc.Select(
                        id=pid("facet_col"),
                        label="Column",
                        clearable=True,
                    ),
                    dmc.NumberInput(
                        id=pid("facet_col_wrap"),
                        label="Wrap",
                        min=0, value=0, max=10, step=1
                    ),
                    dmc.NumberInput(
                        id=pid("facet_row_spacing"),
                        label="Row spacing",
                        min=0.0, value=0.03, max=1, step=0.01, precision=2
                    ),
                    dmc.NumberInput(
                        id=pid("facet_col_spacing"),
                        label="Col spacing",
                        min=0.0, value=0.02, max=1, step=0.01, precision=2
                    )
                ])
            ]),
            make_accordion_items("Marginal", [
                dmc.Group([
                    dmc.Select(
                        id=pid("marginal_x"),
                        label="X",
                        data=make_select_data(["rug", "box", "violin", "histogram"]),
                        clearable=True
                    ),
                    dmc.Select(
                        id=pid("marginal_y"),
                        label="Y",
                        data=make_select_data(["rug", "box", "violin", "histogram"]),
                        clearable=True
                    )
                ])
            ]),
            make_accordion_items("Trendline", [
                dmc.Select(
                    id=pid("trendline"),
                    label="Type",
                    data=make_select_data(["ols", "lowess", "rolling", "expanding", "ewm"]),
                    clearable=True,
                ),
                dmc.Select(
                    id=pid("trendline_scope"),
                    label="Scope",
                    data=make_select_data(["trace", "overall"]),
                    value="trace"
                ),
                dmc.JsonInput(
                    id=pid("trendline_options"),
                    placeholder="ex: {'value1': 'circle-open', 'value2': 'square-open'}",
                    label="Options",
                    value=None,
                    formatOnBlur=True,
                    maxRows=4,
                    autosize=True,
                    debounce=1,
                    validationError="Invalid json"
                )
            ]),
            make_accordion_items("Style", [
                dmc.Group([
                    dmc.Select(
                        id=pid("template"),
                        label="Theme",
                        data=make_select_data(list(pio.templates)),
                        clearable=True,
                        searchable=True,
                        value="seaborn"
                    ),
                    dmc.NumberInput(
                        id=pid("opacity"),
                        label="Opacity",
                        value=0.7,
                        precision=2,
                        min=0.0,
                        max=1.0,
                        step=0.05
                    ),
                    dmc.Select(
                        id=pid("orientation"),
                        label="Orientation",
                        data=[
                            { "label": "vertical", "value": "v" },
                            { "label": "horizontal", "value": "h" }
                        ]
                    ),
                    dmc.Select(
                        id=pid("markers"),
                        label="Markers",
                        data=[
                            { "label": "Show", "value": "True" },
                            { "label": "Hide", "value": "False" }
                        ]
                    )
                ]),
                dmc.Group([
                    dmc.Select(
                        id=pid("color_seq_continuous_scale"),
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
                        id=pid("color_div_continuous_scale"),
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
                        id=pid("color_cyc_continuous_scale"),
                        label="Color cyclical scale",
                        data=make_select_data(
                            ['mygbm', 'mrybm', 'HSV', 'Phase', 'Edge', 'IceFire', 'Twilight']
                        ),
                        clearable=True,
                        searchable=True
                    ),
                    dmc.NumberInput(
                        id=pid("color_continuous_midpoint"),
                        label="Color midpoint",
                        value=None
                    ),
                    dmc.NumberInput(
                        id=pid("size_max"),
                        label="Max size",
                        min=0, step=1, value=20
                    ),
                ]),
                dmc.JsonInput(
                    id=pid("color_discrete_map"),
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
                    id=pid("symbol_map"),
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
                    id=pid("color_discrete_sequence"),
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
                    id=pid("symbol_sequence"),
                    placeholder="ex: {'seq': ['circle-open', 'square-open'] }",
                    label="Symbol sequence (json)",
                    value=None,
                    formatOnBlur=True,
                    maxRows=4,
                    autosize=True,
                    debounce=1,
                    validationError="Invalid json"
                ),
                dmc.JsonInput(
                    id=pid("pattern_shape_map"),
                    placeholder="ex: {'value1': '+', 'value2': '/'}",
                    label="Pattern shape map (json)",
                    value=None,
                    formatOnBlur=True,
                    maxRows=4,
                    autosize=True,
                    debounce=1,
                    validationError="Invalid json"
                ),
                dmc.JsonInput(
                    id=pid("pattern_shape_sequence"),
                    placeholder="ex: {'seq': ['+', '/', '-'] }",
                    label="Pattern shape sequence (json)",
                    value=None,
                    formatOnBlur=True,
                    maxRows=4,
                    autosize=True,
                    debounce=1,
                    validationError="Invalid json"
                ),
                dmc.JsonInput(
                    id=pid("line_dash_map"),
                    placeholder="ex: {'value1': 'dot', 'value2': 'dash'}",
                    label="Line dash map (json)",
                    value=None,
                    formatOnBlur=True,
                    maxRows=4,
                    autosize=True,
                    debounce=1,
                    validationError="Invalid json"
                ),
                dmc.JsonInput(
                    id=pid("line_dash_sequence"),
                    placeholder="ex: {'seq': ['longdash', 'dashdot', 'longdashdot'] }",
                    label="Line dash sequence (json)",
                    value=None,
                    formatOnBlur=True,
                    maxRows=4,
                    autosize=True,
                    debounce=1,
                    validationError="Invalid json"
                ),
            ]),
        ])
    ])

    return res

def make_axis(factory, ax):
    pid = factory

    res = html.Div([
        dmc.Center([
            html.H3(f"{ax.upper()} Axis")
        ]),
        dmc.NumberInput(
            id=pid("axis-index"),
            label="Index",
            min=0,
            step=1,
            max=20,
            value=0,
        ),
        make_accordion([
            make_accordion_items("Title", [
                dmc.Group([
                    dmc.TextInput(
                        id=pid("title_text"),
                        label="Text"
                    ),
                    make_hover_color_picker(pid("title_font_color"))
                ]),
                dmc.NumberInput(
                    id=pid("title_font_size"),
                    label="Size",
                    min=0,
                    step=1,
                    value=14
                ),
                dmc.Select(
                    id=pid("title_font_family"),
                    label="Font",
                    data=make_select_data([
                        "Arial", "Balto", "Courier New", "Droid Sans",
                        "Droid Serif", "Droid Sans Mono", "Gravitas One",
                        "Old Standard TT", "Open Sans", "Overpass",
                        "PT Sans Narrow", "Raleway", "Times New Roman"
                    ]),
                    value="Arial"
                ),
                dmc.NumberInput(
                    id=pid("title_standoff"),
                    label="Standoff",
                    min=0,
                    value=None,
                    precision=2,
                    step=0.01
                )
            ]),
            make_accordion_items("Line", [
                dmc.Group([
                    dmc.Switch(id=pid("visible"), label="Show", checked=True),
                    dmc.NumberInput(id=pid("linewidth"), label="Width",min=0, step=1, value=1),
                    dmc.Select(
                        id=pid("type"),
                        label="Type",
                        data=make_select_data(
                            ["linear", "log", "date", "category", "multicategory"]
                        ),
                    ),
                    make_hover_color_picker(pid("linecolor")),
                ]),
                dmc.Group([
                    dmc.RadioGroup(
                        [dmc.Radio("Top", value="top"), dmc.Radio("Bottom", value="bottom")]
                        if ax == "x" else
                        [dmc.Radio("Left", value="left"), dmc.Radio("Right", value="right")],
                        id=pid("side"),
                        label="Position",
                        value="left" if ax == "x" else "bottom"
                    ),
                    dmc.Select(
                        id=pid("mirror"),
                        label="Mirror",
                        data=make_select_data(["True", "False", "ticks", "all", "allticks"]),
                        value="False"
                    ),
                ])
            ]),
            make_accordion_items("Zero line", [
                dmc.Group([
                    dmc.Switch(id=pid("zeroline"), label="Show", checked=False),
                    make_hover_color_picker(pid("zerolinecolor")),
                    dmc.NumberInput(id=pid("zerolinewidth"), label="Width",min=0, step=1, value=1),
                ])
            ]),
            make_accordion_items("Grid", [
                dmc.Group([
                    dmc.Switch(id=pid("showgrid"), label="Show", checked=False),
                    dmc.NumberInput(id=pid("gridwidth"), label="Width", min=0, step=1, value=1),
                    dmc.Select(
                        id=pid("griddash"),
                        label="Dash",
                        data=make_select_data([
                            "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
                        ]),
                        value="solid"
                    ),
                    make_hover_color_picker(pid("gridcolor")),
                ])
            ]),
            make_accordion_items("Tick Labels", [
                dmc.Group([
                    dmc.Switch(id=pid("showticklabels"), label="Show", checked=True),
                    dmc.Switch(id=pid("automargin"), label="Automargin", checked=True),
                ]),
                dmc.Group([
                    dmc.Select(
                        id=pid("tickangle"),
                        label="Angle",
                        data=make_select_data(["0", "45", "90", "135", "180", "-45", "-90", "-135", "-180"]),
                        value="0"
                    ),
                    dmc.Select(
                        id=pid("ticklabelposition"),
                        label="Position",
                        data=make_select_data([
                            "outside", "inside", "outside top", "inside top",
                            "outside left", "inside left", "outside right", "inside right",
                            "outside bottom", "inside bottom"
                        ])
                    ),

                    dmc.NumberInput(label="Size", id=pid("tickfont_size"), min=0, value=14, step=1),
                    dmc.Select(
                        id=pid("tickfont_family"),
                        label="Font",
                        data=make_select_data([
                            "Arial", "Balto", "Courier New", "Droid Sans",
                            "Droid Serif", "Droid Sans Mono", "Gravitas One",
                            "Old Standard TT", "Open Sans", "Overpass",
                            "PT Sans Narrow", "Raleway", "Times New Roman"
                        ]),
                        value="Arial"
                    ),
                    make_hover_color_picker(pid("tickfont_color"))
                ])
            ]),
            make_accordion_items("Tick Markers", [
                dmc.Group([
                    dmc.RadioGroup(
                        [
                            dmc.Radio("Inside", value="inside"),
                            dmc.Radio("Outside", value="outside"),
                            dmc.Radio("Hide", "")
                        ],
                        id=pid("ticks"),
                        label="Position",
                        value="outside"
                    ),
                    dmc.NumberInput(label="Length", id=pid("ticklen"), min=0, step=1, value=1),
                    dmc.NumberInput(label="Width", id=pid("tickwidth"), min=0, step=1, value=1),
                    dmc.NumberInput(label="Max markers", id=pid("nticks"), min=0, step=1, value=10),
                    make_hover_color_picker(pid("tickcolor"))
                ])
            ]),
        ])
    ])
    return res

import pprint
def make_axis_callbacks(factory, ax, figure_id):
    pid = factory
    @callback(
        Output(figure_id, "figure"),
        inputs=dict(inputs=(
            State(pid("axis-index"), "value"),
            Input(pid("title_text"), "value"),
            Input(pid("title_font_size"), "value"),
            Input(pid("title_font_color"), "value"),
            Input(pid("title_font_family"), "value"),
            Input(pid("title_standoff"), "value"),
            Input(pid("visible"), "checked"),
            Input(pid("type"), "value"),
            Input(pid("side"), "value"),
            Input(pid("linewidth"), "value"),
            Input(pid("linecolor"), "value"),
            Input(pid("mirror"), "value"),
            Input(pid("showgrid"), "checked"),
            Input(pid("griddash"), "value"),
            Input(pid("gridwidth"), "value"),
            Input(pid("gridcolor"), "value"),
            Input(pid("showticklabels"), "checked"),
            Input(pid("tickangle"), "value"),
            Input(pid("ticklabelposition"), "value"),
            Input(pid("tickfont_family"), "value"),
            Input(pid("tickfont_size"), "value"),
            Input(pid("tickfont_color"), "value"),
            Input(pid("automargin"), "checked"),
            Input(pid("ticks"), "value"),
            Input(pid("ticklen"), "value"),
            Input(pid("tickwidth"), "value"),
            Input(pid("nticks"), "value"),
            Input(pid("tickcolor"), "value"),
            Input(pid("zeroline"), "checked"),
            Input(pid("zerolinecolor"), "value"),
            Input(pid("zerolinewidth"), "value"),
        )),
        prevent_initial_callbacks=True,
    )
    def update_axis(inputs):
        if ax == "x":
            n = "xaxis" if inputs[0] == 0 else f"xaxis{inputs[0]+1}"
            return patch_figure(ctx, ["layout", n])
        elif ax == "y":
            n = "yaxis" if inputs[0] == 0 else f"yaxis{inputs[0]+1}"
            return patch_figure(ctx, ["layout", n])
        return no_update


def make_axes(factory):
    pid = factory.child("rangeslider")

    res = html.Div([
        dmc.Grid([
            dmc.Col(make_axis(factory.child("xaxis"), "x"), span=6),
            dmc.Col(make_axis(factory.child("yaxis"), "y"), span=6),
        ]),
        make_accordion([
            make_accordion_items("Range slider", [
                dmc.Group([
                    dmc.Switch(id=pid("rangeslider_visible"), label="Show", checked=False),
                    dmc.NumberInput(label="Width", id=pid("rangeslider_borderwidth"), min=0, step=1, value=1),
                    dmc.NumberInput(label="Thickness", id=pid("rangeslider_thickness"), min=0, max=1, precision=2, step=0.01, value=0.1),
                    dmc.RadioGroup(
                        [
                            dmc.Radio("Auto", value="auto"),
                            dmc.Radio("Fixed", value="fixed"),
                            dmc.Radio("Match", value="match")
                        ],
                        id=pid("rangeslider_yaxis_rangemode"),
                        label="Mode",
                        value="auto",
                    ),
                    make_hover_color_picker(pid("rangeslider_bordercolor"), "Border color"),
                    make_hover_color_picker(pid("rangeslider_bgcolor"), "Background color")
                ])
            ]),
        ])
    ])
    return res



def make_axes_callbacks(factory, figure_id):

    make_axis_callbacks(factory.child("xaxis"), "x", figure_id)
    make_axis_callbacks(factory.child("yaxis"), "y", figure_id)

    pid = factory.child("rangeslider")

    @callback(
        Output(figure_id, "figure"),
        inputs=dict(inputs=(
            State(factory.child("xaxis")("axis-index"), "value"),
            Input(pid("rangeslider_visible"), "checked"),
            Input(pid("rangeslider_borderwidth"), "value"),
            Input(pid("rangeslider_thickness"), "value"),
            Input(pid("rangeslider_bordercolor"), "value"),
            Input(pid("rangeslider_bgcolor"), "value"),
            Input(pid("rangeslider_yaxis_rangemode"), "value"),
        )),
        prevent_initial_callbacks=True,
    )
    def update_rs(inputs):
        n = "xaxis" if inputs[0] == 0 else f"xaxis{inputs[0]+1}"
        return patch_figure(ctx, ["layout", n])

def make_plot(factory):
    pid = factory
    res =  html.Div([
        dcc.Graph(
            figure=blank_figure(),
            id=pid.sid("figure"),
            responsive=True,
            mathjax=True,
            style = {"margin-left": "auto", "margin-right": "auto", "height":"70vh", "width":"90%"}
        ),
        html.Div([
            dmc.Group([
                dmc.Select(
                    id=pid.sid("select-preset"),
                    placeholder="Select preset",
                    clearable=True
                ),
            ])
        ], id=pid.sid("presets-div")),
        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab("Trace", value="trace", disabled=False,   id=pid.sid("trace-tab")),
                dmc.Tab("Title", value="title", disabled=False,   id=pid.sid("title-tab")),
                dmc.Tab("Axes", value="axes", disabled=False,     id=pid.sid("axes-tab")),
                dmc.Tab("Legend", value="legend", disabled=False, id=pid.sid("legend-tab"))
            ]),
            dmc.TabsPanel(make_trace(pid.child("trace")), value="trace"),
            dmc.TabsPanel(make_plot_title(pid.child("title")), value="title"),
            dmc.TabsPanel(make_axes(pid.child("axes")), value="axes"),
            dmc.TabsPanel(make_plot_legend(pid.child("legend")), value="legend")
        ], value="trace")
    ])

    return res

def make_plot_callbacks(factory):
    pid = factory
    figure_id = pid.sid("figure")
    make_plot_title_callbacks(pid.child("title"), figure_id),
    make_plot_legend_callbacks(pid.child("legend"), figure_id)
    make_axes_callbacks(pid.child("axes"), figure_id)

