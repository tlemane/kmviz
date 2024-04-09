from dash_extensions.enrich import Input, Output, State, html, ctx, callback, dcc
from dash import Patch, no_update
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash_iconify import DashIconify
from kmviz.ui.utils import make_select_data, prevent_update_on_none, prevent_update_on_empty, icons, KMVIZ_ICONS
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
                            color: str=dict(rgb=dict(r=0,g=0,b=0,a=0.9)),
                            icon="noto:artist-palette"):
    target = f"{id['type']}-{id['index']}-pop"
    return html.Div([
        DashIconify(id=target, icon=icon, width=30, style = {"margin":"auto"}),
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

def make_nb_input(id, label: str, params: tuple, precision=None, **kwargs):
    return dmc.NumberInput(
        id=id,
        label=label,
        min=params[0],
        step=params[1],
        max=params[2],
        value=params[3],
        precision=precision,
        className="kmviz-dmc-number-input",
        **kwargs,
    )

def make_text_input(id, label: str, value=None, **kwargs):
    return dmc.TextInput(
        id=id,
        label=label,
        value=value,
        icon=icons("text"),
        className="kmviz-dmc-text-input",
        **kwargs
    )

def make_select_input(id, label, data=[], value=None, **kwargs):
    return dmc.Select(
        id=id,
        label=label,
        data=data,
        value=value,
        className="kmviz-dmc-figure-select",
        **kwargs
    )

def make_font_input(id, label, **kwargs):
    data = make_select_data([
        "Arial", "Balto", "Courier New", "Droid Sans",
        "Droid Serif", "Droid Sans Mono", "Gravitas One",
        "Old Standard TT", "Open Sans", "Overpass",
        "PT Sans Narrow", "Raleway", "Times New Roman"
    ])

    return make_select_input(id, label, data, "Arial", icon=icons("family"), **kwargs)


def magic_json(d: dict):
    c = d.copy()
    for k, v in d.items():
        if "_" in k:
            sk, sv = k.split("_", 1)
            if sk not in c:
                c[sk] = {}
            if isinstance(v, dict):
                v = magic_json(v)
            c[sk][sv] = v
            c[sk] = magic_json(c[sk])
            del c[k]
    return c

def from_json(value, p=None):
    try:
        value = json.loads(value)
        if p:
            value = value[p]
        return value
    except:
        return None

def color_to_string(c):
    if not c:
        return c
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

def patch_figure_all(context, paths = ["layout"], skip = set()):
    args = context.args_grouping
    p = Patch(paths)
    for e in args["inputs"]:
        if e["str_id"] not in skip:
            if (isinstance(e["value"], list) and not e["value"]) or e["value"] is None:
                continue

            if isinstance(e["value"], dict):
                e["value"] = color_to_string(e["value"])
            patch_value_id(p, e["id"], e["value"])
    return p

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

    return html.Div([
            dmc.Group([
                make_text_input(
                    pid("title_text"),
                    "Title",
                    placeholder="<b>Title</b>"
                ),
                make_nb_input(
                    pid("title_font_size"),
                    "Size",
                    (1, 1, 100, 16),
                    icon=icons("font_size"),
                ),
                make_font_input(
                    pid("title_font_family"),
                    "Font",
                ),
                make_hover_color_picker(
                    pid("title_font_color"),
                    "Font",
                    color=dict(hex="#000000"),
                    icon=KMVIZ_ICONS["ctext"]),
            ]),
            dmc.Group([
                make_select_input(
                    pid("title_xanchor"),
                    "Anchor X",
                    make_select_data(["auto", "left", "center", "right"]),
                    value="center",
                    icon=icons("single")
                ),
                make_select_input(
                    pid("title_xref"),
                    "Ref X",
                    make_select_data(["container", "paper"]),
                    value="container",
                    icon=icons("single")
                ),
                make_nb_input(
                    pid("title_x"),
                    "x",
                    (0.0, 0.01, 1.0, 0.5),
                    2,
                    icon=icons("floating"),
                ),
                make_select_input(
                    pid("title_yanchor"),
                    "Anchor Y",
                    make_select_data(["auto", "top", "middle", "bottom"]),
                    value="top",
                    icon=icons("single")
                ),
                make_select_input(
                    pid("title_yref"),
                    "Ref Y",
                    make_select_data(["container", "paper"]),
                    value="container",
                    icon=icons("single")
                ),
                make_nb_input(
                    pid("title_y"),
                    "y",
                    (0.0, 0.01, 1.0, 0.95),
                    2,
                    icon=icons("floating")
                )
            ]),
        ])
    #])


def make_plot_title_callbacks(factory, figure_id):
    pid = factory

    @callback(
        Output(figure_id, "figure", allow_duplicate=True),
        inputs=dict(inputs=(
            Input(figure_id, "figure"),
            Input("kmviz-auto-apply", "checked"),
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
        if ctx.triggered_id == figure_id:
            if not inputs[1]:
                return no_update
            return patch_figure_all(ctx, ["layout"], set([figure_id, "kmviz-auto-apply"]))
        return patch_figure(ctx)

def make_plot_shape(factory):
    pid = factory

    res = html.Div([
        dmc.JsonInput(
            id=pid("shapes"),
            placeholder='ex: { "shapes": [ { "type": "circle", "x0": 0, "x1": 2, "y0": 0.1, "y1": 0.8 } ] }',
            label="Shape parameters",
            value=None,
            autosize=True,
            debounce=2,
            validationError="Invalid json",
            icon=icons("json")
        ),
    ])

    return res

def make_plot_shape_callbacks(factory, figure_id):
    pid = factory
    @callback(
        Input(pid("shapes"), "value"),
        Output(figure_id, "figure"),
        prevent_initial_call=True
    )
    def add_shapes(shapes):
        p = Patch()
        if not shapes:
            p["layout"]["shapes"] = []
        js = from_json(shapes, "shapes")
        if not js:
            return no_update
        all_shapes = [magic_json(x) for x in js]
        p["layout"]["shapes"] = all_shapes
        return p

def make_plot_legend(factory):
    pid = factory

    title_panel = dmc.TabsPanel(value="title", children = [
        dmc.Group([
            make_text_input(
                pid("legend_title_text"),
                "Text",
                placeholder="<b>Legend title</b>"
            ),
            make_nb_input(
                pid("legend_title_font_size"),
                "Size",
                (0, 1, 100, 13),
                icon=icons("font_size")
            ),
            make_font_input(
                pid("legend_title_font_family"),
                "Font",
            ),
            make_select_input(
                pid("legend_title_side"),
                "Position",
                make_select_data(["top", "left", "top left", "top center", "top right"]),
                value="top",
                icon=icons("pos")
            ),
            make_hover_color_picker(
                id=pid("legend_title_font_color"),
                color=dict(hex="#000000"),
                icon=KMVIZ_ICONS["ctext"]
            ),
        ]),
    ])

    position_panel = dmc.TabsPanel(value="position", children = [
        dmc.Group([
            dmc.SegmentedControl(
                id=pid("legend_orientation"),
                data=[{"label":"vertical", "value":"v" }, {"label":"horizontal", "value":"h"}],
                value="v"
            ),
            make_nb_input(
                pid("legend_indentation"),
                "Indentation",
                (-15, 1, 100, 0),
                icon=icons("indent")
            ),
            make_select_input(
                pid("legend_xanchor"),
                "Anchor X",
                make_select_data(["auto", "left", "center", "right"]),
                #value="auto",
                icon=icons("single")
            ),
            make_select_input(
                pid("legend_xref"),
                "Ref X",
                make_select_data(["container", "paper"]),
                #value="container",
                icon=icons("single")
            ),
            make_nb_input(
                pid("legend_x"),
                "x",
                (0.0, 0.01, 1.0, None),
                2,
                icon=icons("floating"),
                placeholder="0.5",
                startValue=0.9
            ),
            make_select_input(
                pid("legend_yanchor"),
                "Anchor Y",
                make_select_data(["auto", "top", "middle", "bottom"]),
                #value="auto",
                icon=icons("single"),
            ),
            make_select_input(
                pid("legend_yref"),
                "Ref Y",
                make_select_data(["container", "paper"]),
                #value="container",
                icon=icons("single")
            ),
            make_nb_input(
                pid("legend_y"),
                "y",
                (0.0, 0.01, 1.0, None),
                2,
                icon=icons("floating"),
                placeholder="0.95",
                startValue=0.9
            )
        ]),

    ])

    entry_panel = dmc.TabsPanel(value="entry", children = [
        dmc.Group([
            make_font_input(
                pid("legend_font_family"),
                "Font",
            ),
            make_nb_input(
                pid("legend_font_size"),
                "Size",
                (0, 1, 100, 10),
                icon=icons("font_size")
            ),
            make_hover_color_picker(
                pid("legend_font_color"),
                color=dict(hex="#000000"),
                icon=KMVIZ_ICONS["ctext"]
            )
        ]),
    ])
    box_panel = dmc.TabsPanel(value="box", children = [
        dmc.Group([
            make_nb_input(
                pid("legend_borderwidth"),
                "Width",
                (0, 1, 100, 0),
                icon=icons("width", rotate=1)
            ),
            make_hover_color_picker(
                pid("legend_bordercolor"),
                "Border",
                icon=KMVIZ_ICONS["cline"],
                color=None
            ),
            make_hover_color_picker(
                pid("legend_bgcolor"),
                "Background",
                icon=KMVIZ_ICONS["cback"],
                color=None
            ),
        ])
    ])


    res = dmc.Tabs([
        dmc.TabsList([
            dmc.Tab("Title", value="title"),
            dmc.Tab("Position", value="position"),
            dmc.Tab("Entry", value="entry"),
            dmc.Tab("Box", value="box"),
            dmc.Switch(
                id=pid("showlegend"),
                checked=True,
                size="xs",
                style={"margin-top":"10px"}
            ),
        ]),
        dmc.Space(h=10),
        title_panel,
        position_panel,
        entry_panel,
        box_panel,
    ], value = "title")

    return res

def make_color_legend(factory):
    pid = factory

    title_panel = dmc.TabsPanel(value="title", children = [
        dmc.Group([
            make_text_input(
                pid("colorbar_title_text"),
                "Text",
            ),
            make_nb_input(
                pid("colorbar_title_font_size"),
                "Size",
                (0, 1, 100, 13),
                icon=icons("font_size")
            ),
            make_font_input(
                pid("colorbar_title_font_family"),
                "Font",
            ),
            make_select_input(
                pid("colorbar_title_side"),
                "Position",
                make_select_data(["top", "right", "bottom"]),
                value="top",
                icon=icons("pos")
            ),
            make_hover_color_picker(
                id=pid("colorbar_title_font_color"),
                color=dict(hex="#000000"),
                icon=KMVIZ_ICONS["ctext"]
            ),
        ]),
    ])

    box_panel = dmc.TabsPanel(value="box", children = [
        dmc.Group([
            make_nb_input(
                pid("colorbar_x"),
                "x",
                (-10.0, 0.01, 10.0, 1),
                2,
                icon=icons("floating"),
            ),
            make_nb_input(
                pid("colorbar_y"),
                "y",
                (-10.0, 0.01, 10.0, 0.5),
                2,
                icon=icons("floating")
            ),
            make_nb_input(
                pid("colorbar_borderwidth"),
                "Width",
                (0, 1, 100, 0),
                icon=icons("width", rotate=1)
            ),
            make_hover_color_picker(
                pid("colorbar_bordercolor"),
                "Border",
                icon=KMVIZ_ICONS["cline"]
            ),
            make_hover_color_picker(
                pid("colorbar_bgcolor"),
                "Background",
                icon=KMVIZ_ICONS["cback"]
            ),
        ])
    ])

    res = dmc.Tabs([
        dmc.TabsList([
            dmc.Tab("Title", value="title"),
            dmc.Tab("Box", value="box"),
        ]),
        dmc.Space(h=10),
        title_panel,
        box_panel,
    ], value = "title")

    return res


def make_plot_legend_callbacks(factory, figure_id):

    pid = factory

    @callback(
        Output(figure_id, "figure", allow_duplicate=True),
        inputs=dict(inputs=(
            Input(figure_id, "figure"),
            Input("kmviz-auto-apply", "checked"),
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
        if ctx.triggered_id == figure_id:
            if not inputs[1]:
                return no_update
            return patch_figure_all(ctx, ["layout"], set([figure_id, "kmviz-auto-apply"]))
        return patch_figure(ctx)


def make_color_legend_callbacks(factory, figure_id):

    pid = factory

    @callback(
        Output(figure_id, "figure", allow_duplicate=True),
        inputs=dict(inputs=(
            Input(pid("colorbar_title_text"), "value"),
            Input(pid("colorbar_title_font_size"), "value"),
            Input(pid("colorbar_title_font_family"), "value"),
            Input(pid("colorbar_title_font_color"), "value"),
            Input(pid("colorbar_title_side"), "value"),
            Input(pid("colorbar_borderwidth"), "value"),
            Input(pid("colorbar_bordercolor"), "value"),
            Input(pid("colorbar_bgcolor"), "value"),
            Input(pid("colorbar_x"), "value"),
            Input(pid("colorbar_y"), "value"),
        )),
        prevent_initial_call=True,
        prevent_initial_callbacks= True
    )
    def update_legend(inputs):
        return patch_figure(ctx, ["layout", "coloraxis"])


def make_trace(factory):
    pid = factory

    data_panel = dmc.TabsPanel(value="data", children=[
        dmc.Group([
            dmc.MultiSelect(id=pid("xselect"), label="X", value=[]),
            dmc.MultiSelect(id=pid("yselect"), label="Y", value=[]),
            dmc.MultiSelect(id=pid("zselect"), label="Z", value=[]),
            make_select_input(id=pid("color"), label="Color", clearable=True, searchable=True),
            make_select_input(id=pid("size"), label="Size", clearable=True, searchable=True),
            make_select_input(id=pid("text"), label="Text", clearable=True, searchable=True),
            make_select_input(id=pid("symbol"), label="Symbol", clearable=True, searchable=True),
            make_select_input(id=pid("pattern_shape"), label="Pattern shape", clearable=True, searchable=True),
            make_select_input(id=pid("base"), label="Base", clearable=True, searchable=True),
            make_select_input(id=pid("line_dash"), label="Line dash", clearable=True, searchable=True),
            make_select_input(id=pid("line_group"), label="Line group", clearable=True, searchable=True),
            dmc.MultiSelect(id=pid("dimensions"), label="Dimensions", clearable=True, searchable=True),
            make_select_input(id=pid("values"), label="Values", clearable=True, searchable=True),
            make_select_input(id=pid("names"), label="Names", clearable=True, searchable=True),
        ])
    ])

    anim_panel = dmc.TabsPanel(value="anim", children=[
        dmc.Group([
            make_select_input(id=pid("animation_frame"), label="Frame", clearable=True, searchable=True),
            make_select_input(id=pid("animation_group"), label="Group", clearable=True, searchable=True)
        ])
    ])

    dist_panel = dmc.TabsPanel(value="dist", children=[
        dmc.Group([
            make_select_input(
                id=pid("violinmode"),
                label="Violin mode",
                value="group",
                data=make_select_data([
                    "group", "overlay"
                ]),
                clearable=True,
                searchable=True,
            ),
            make_select_input(
                id=pid("boxmode"),
                label="Box mode",
                value="group",
                data=make_select_data([
                    "group", "overlay"
                ]),
                clearable=True,
                searchable=True,
            ),
            make_select_input(
                id=pid("points"),
                label="Points",
                value="outliers",
                data=make_select_data([
                    "outliers", "suspectedoutliers", "all", "False"
                ]),
                clearable=True,
                searchable=True,
            ),
            make_select_input(
                id=pid("box"),
                label="Violin box",
                value="False",
                data=make_select_data([
                    "True", "False"
                ]),
                clearable=True,
                searchable=True,
            ),
            make_select_input(
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
    ])

    dens_panel = dmc.TabsPanel(value="dens", children=[
        dmc.Group([
            make_select_input(
                id=pid("histfunc"),
                label="Hist function",
                value="count",
                data=make_select_data([
                    "count", "sum", "avg", "min", "max"
                ]),
                clearable=True,
                searchable=True,
            ),
            make_select_input(
                id=pid("histnorm"),
                label="Hist norm",
                data=make_select_data([
                    "percent", "probability", "density", "probability density"
                ]),
                clearable=True,
                searchable=True,
            ),

            make_nb_input(
                pid("nbinsx"),
                "X bins",
                (0, 1, 1000, 4),
                icon=icons("integer")
            ),
            make_nb_input(
                pid("nbinsy"),
                "Y bins",
                (0, 1, 1000, 4),
                icon=icons("integer")
            ),
            make_select_input(
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
    ])

    facet_panel = dmc.TabsPanel(value="facet", children=[
        dmc.Group([
            make_select_input(
                id=pid("facet_row"),
                label="Row",
                clearable=True,
            ),
            make_select_input(
                id=pid("facet_col"),
                label="Column",
                clearable=True,
            ),
            make_nb_input(
                pid("facet_col_wrap"),
                "Wrap",
                (0, 1, 10, 0),
                icon=icons("integer")
            ),
            make_nb_input(
                pid("facet_row_spacing"),
                "Row spacing",
                (0.0, 0.01, 1, 0.03),
                2,
                icon=icons("floating")
            ),
            make_nb_input(
                pid("facet_col_spacing"),
                "Col spacing",
                (0.0, 0.01, 1, 0.03),
                2,
                icon=icons("integer"),
            )
        ])

    ])

    marg_panel = dmc.TabsPanel(value="marg", children=[
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
    ])

    trend_panel = dmc.TabsPanel(value="trend", children=[
        dmc.Group([
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
                validationError="Invalid json",
                icon=icons("json")
            )
        ])
    ])

    style_panel = dmc.TabsPanel(value="style", children = [
        dmc.Group([
            make_select_input(
                 id=pid("barmode"),
                 label="Bar mode",
                 clearable=True,
                 searchable=True,
                 data=make_select_data(["relative", "group", "overlay"])
            ),
            make_select_input(
                 id=pid("line_shape"),
                 label="Line shape",
                 clearable=True,
                 searchable=True,
                 data=make_select_data(["hv", "vh", "hvh", "vhv", "spline", "linear"])
            ),
            make_select_input(
                id=pid("orientation"),
                label="Orientation",
                data=[
                    { "label": "vertical", "value": "v" },
                    { "label": "horizontal", "value": "h" }
                ]
            ),
            make_select_input(
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
                id=pid("template"),
                label="Theme",
                data=make_select_data(list(pio.templates)),
                clearable=True,
                searchable=True,
                value="seaborn",
                icon=icons("style")
            ),
            make_select_input(
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
                searchable=True,
                icon=icons("picker")
            ),
            make_select_input(
                id=pid("color_div_continuous_scale"),
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
                id=pid("color_cyc_continuous_scale"),
                label="Color cyclical scale",
                data=make_select_data(
                    ['mygbm', 'mrybm', 'HSV', 'Phase', 'Edge', 'IceFire', 'Twilight']
                ),
                clearable=True,
                searchable=True,
                icon=icons("picker"),
            ),
            make_nb_input(
                pid("color_continuous_midpoint"),
                "Color midpoint",
                (None, None, None, None),
                icon=icons("floating")
            ),
            make_nb_input(
                pid("opacity"),
                "Opacity",
                (0.0, 0.01, 1.0, 0.7),
                2,
                icon=icons("floating")
            ),
            make_nb_input(
                pid("size_max"),
                "Max size",
                (0, 1, 50, 15),
                icon=icons("integer"),
            ),
        ]),
        dmc.Group([
            dmc.JsonInput(
                id=pid("color_discrete_map"),
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
                id=pid("symbol_map"),
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
                id=pid("color_discrete_sequence"),
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
                id=pid("symbol_sequence"),
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
        ], grow=True),
        dmc.Group([
            dmc.JsonInput(
                id=pid("pattern_shape_map"),
                placeholder="ex: {'value1': '+', 'value2': '/'}",
                label="Pattern shape map (json)",
                value=None,
                formatOnBlur=True,
                maxRows=4,
                autosize=True,
                debounce=1,
                validationError="Invalid json",
                icon=icons("json")
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
                validationError="Invalid json",
                icon=icons("json")
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
                validationError="Invalid json",
                icon=icons("json")
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
                validationError="Invalid json",
                icon=icons("json")
            ),
        ], grow=True)
    ])

    trace_type = make_select_input(
        pid("type"),
        None,
        data=make_select_data([
            "Scatter",
            "Line",
            "Area",
            "Bar",
            #"Scatter3D",
            "Parallel categories",
            "Parallel coordinates",
            "Scatter matrix",
            "Density heatmap",
            "Density contour",
            "Violin",
            "Box"
        ]),
        style={"width":"160px"},
        placeholder="Type",
        icon=icons("plot")
    )


    trace_tab = dmc.Tabs([
        dmc.TabsList([
            trace_type,
            dmc.Tab("Data", value="data"),
            dmc.Tab("Animation", value="anim"),
            dmc.Tab("Distribution", value="dist"),
            dmc.Tab("Density", value="dens"),
            dmc.Tab("Facet", value="facet"),
            dmc.Tab("Marginal", value="marg"),
            dmc.Tab("Trendline", value="trend"),
            dmc.Tab("Style", value="style")
        ]),
        data_panel,
        anim_panel,
        dist_panel,
        dens_panel,
        facet_panel,
        marg_panel,
        trend_panel,
        style_panel
    ])

    return trace_tab

def make_axis(factory, ax):
    pid = factory

    title_panel = dmc.TabsPanel(value="title", children = [
        dmc.Group([
            make_text_input(
                pid("title_text"),
                "Text",
                placeholder="<b>Title</b>"
            ),
            make_nb_input(
                pid("title_font_size"),
                "Size",
                (0, 1, 100, None),
                icon=icons("font_size"),
                placeholder="14"
            ),
            make_font_input(
                pid("title_font_family"),
                "Font",
            ),
            make_nb_input(
                pid("title_standoff"),
                "Standoff",
                (0, 0.01, None, None),
                2,
                icon=icons("floating")
            ),
            make_hover_color_picker(pid("title_font_color"), icon=KMVIZ_ICONS["ctext"], color=None),
        ]),
    ])

    line_panel = dmc.TabsPanel(value="line", children = [
        dmc.Group([
            dmc.Switch(
                id=pid("visible"),
                size="lg",
                onLabel="ON",
                offLabel="OFF",
                checked=True
            ),
            dmc.SegmentedControl(
                data= make_select_data(["top", "bottom"], True)
                      if ax == "x" else
                      make_select_data(["left", "right"], True)
                ,
                fullWidth=True,
                id=pid("side"),
                value="left" if ax == "x" else "bottom",
                size="xs",
                color="#1C7ED6"
            ),

            make_nb_input(
                pid("linewidth"),
                "Width",
                (0, 1, None, 0),
                icon=icons("width", rotate=1)
            ),
            make_select_input(
                pid("type"),
                "Type",
                make_select_data(["linear", "log", "date", "category", "multicategory"]),
                icon=icons("axis")
            ),
            make_select_input(
                pid("mirror"),
                "Mirror",
                make_select_data(["True", "False", "ticks", "all", "allticks"]),
                "False",
                icon=icons("single")
            ),
            make_hover_color_picker(pid("linecolor"), icon=KMVIZ_ICONS["cline"], color=None),
        ]),
    ])

    zero_panel = dmc.TabsPanel(value="zeroline", children = [
        dmc.Group([
            dmc.Switch(
                id=pid("zeroline"),
                size="lg",
                onLabel="ON",
                offLabel="OFF",
                checked=False
            ),
            make_nb_input(
                pid("zerolinewidth"),
                "Width",
                (0, 1, None, 1),
                icon=icons("width", rotate=1)
            ),
            make_hover_color_picker(
                pid("zerolinecolor"),
                icon=KMVIZ_ICONS["cline"],
                color=None
            ),
        ])
    ])

    grid_panel = dmc.TabsPanel(value="grid", children = [
        dmc.Group([
            dmc.Switch(
                id=pid("showgrid"),
                size="lg",
                onLabel="ON",
                offLabel="OFF",
                checked=True
            ),
            make_nb_input(
                pid("gridwidth"),
                "Width",
                (0, 1, None, 1),
                icon=icons("width", rotate=1)
            ),
            make_select_input(
                pid("griddash"),
                "Dash",
                data=make_select_data([
                    "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
                ]),
                value="solid",
                icon=icons("dash")
            ),
            make_hover_color_picker(pid("gridcolor"), icon=KMVIZ_ICONS["cline"], color=None),
        ])
    ])

    label_panel = dmc.TabsPanel(value="ticklabels", children = [
        dmc.Group([
            dmc.Switch(
                id=pid("showticklabels"),
                onLabel="ON",
                offLabel="OFF",
                size="lg",
                checked=True
            ),
            dmc.Switch(
                id=pid("automargin"),
                onLabel="Automargin",
                offLabel="Automargin",
                size="lg",
                checked=True
            ),
            make_nb_input(
                pid("tickangle"),
                "Angle",
                (-180, 1, 180, None),
                icon=icons("angle")
            ),
            make_select_input(
                pid("ticklabelposition"),
                "Position",
                data=make_select_data([
                    "outside", "inside", "outside top", "inside top",
                    "outside left", "inside left", "outside right", "inside right",
                    "outside bottom", "inside bottom"
                ]),
                icon=icons("pos")
            ),
            make_nb_input(
                pid("tickfont_size"),
                "Size",
                (0, 1, 100, None),
                icon=icons("font_size")
            ),
            make_font_input(
                pid("tickfont_family"),
                "Font",
            ),
            make_hover_color_picker(pid("tickfont_color"), icon=KMVIZ_ICONS["ctext"], color=None)
        ])
    ])

    marker_panel = dmc.TabsPanel(value="tickmarkers", children = [
        dmc.Group([
            dmc.SegmentedControl(
                data=make_select_data(["inside", "outside", "hide"], True),
                fullWidth=True,
                id=pid("ticks"),
                size="xs",
                value="hide",
                color="#1C7ED6"
            ),
            make_nb_input(
                pid("ticklen"),
                "Length",
                (0, 1, 100, 1),
                icon=icons("width", rotate=1)
            ),
            make_nb_input(
                pid("tickwidth"),
                "Width",
                (0, 1, 100, 1),
                icon=icons("width")
            ),
            make_nb_input(
                pid("nticks"),
                "Max",
                (0, 1, 1000, None),
                icon=icons("nindex")
            ),
            make_hover_color_picker(pid("tickcolor"), icon=KMVIZ_ICONS["cline"], color=None)
        ])
    ])


    res = dmc.Tabs([
        dmc.TabsList([
            icons(
                "X" if ax == "x" else "Y",
                color="#1C7ED6",
                width=30
            ),
            dmc.Tab("Title", value="title"),
            dmc.Tab("Line", value="line"),
            dmc.Tab("Zeroline", value="zeroline"),
            dmc.Tab("Grid", value="grid"),
            dmc.Tab("Ticks labels", value="ticklabels"),
            dmc.Tab("Ticks markers", value="tickmarkers"),
            dmc.NumberInput(
                id=pid("axis-index"),
                min=0, step=1, max=20, value=0,
                size="xs",
                style = {"width": "55px", "height": "20px", "margin-top": "1px"}
            ),
        ]),
        title_panel,
        line_panel,
        zero_panel,
        grid_panel,
        label_panel,
        marker_panel
    ], value = "title")

    return res


    res = html.Div([
        dmc.Center([
            html.H3(f"{ax.upper()} Axis")
        ]),
        make_nb_input(
            pid("axis-index"),
            "Axis",
            (0, 1, 20, 0),
            icon=icons("nindex")
        ),
        make_accordion([
            make_accordion_items("Title", [
                dmc.Group([
                    make_text_input(
                        pid("title_text"),
                        "Text"
                    ),
                    make_nb_input(
                        pid("title_font_size"),
                        "Size",
                        (0, 1, 100, None),
                        startValue=16,
                        icon=icons("font_size"),
                        placeholder="14"
                    ),
                    make_font_input(
                        pid("title_font_family"),
                        "Font",
                    ),
                    make_nb_input(
                        pid("title_standoff"),
                        "Standoff",
                        (0, 0.01, None, None),
                        2,
                        icon=icons("floating")
                    ),
                    make_hover_color_picker(pid("title_font_color"), icon=KMVIZ_ICONS["ctext"], color=None),
                ]),
            ]),
            make_accordion_items("Line", [
                dmc.Group([
                    dmc.Switch(
                        id=pid("visible"),
                        size="lg",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    ),
                    dmc.SegmentedControl(
                        data= make_select_data(["top", "bottom"], True)
                              if ax == "x" else
                              make_select_data(["left", "right"], True)
                        ,
                        fullWidth=True,
                        id=pid("side"),
                        #value="left" if ax == "x" else "bottom",
                        size="xs",
                        color="#1C7ED6"
                    ),

                    make_nb_input(
                        pid("linewidth"),
                        "Width",
                        (0, 1, None, 1),
                        icon=icons("width", rotate=1)
                    ),
                    make_select_input(
                        pid("type"),
                        "Type",
                        make_select_data(["linear", "log", "date", "category", "multicategory"]),
                        icon=icons("axis")
                    ),
                    make_select_input(
                        pid("mirror"),
                        "Mirror",
                        make_select_data(["True", "False", "ticks", "all", "allticks"]),
                        icon=icons("single")
                    ),
                    make_hover_color_picker(pid("linecolor"), icon=KMVIZ_ICONS["cline"]),
                ]),
            ]),
            make_accordion_items("Zero line", [
                dmc.Group([
                    dmc.Switch(
                        id=pid("zeroline"),
                        size="lg",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    ),
                    make_nb_input(
                        pid("zerolinewidth"),
                        "Width",
                        (0, 1, None, 1),
                        icon=icons("width", rotate=1)
                    ),
                    make_hover_color_picker(
                        pid("zerolinecolor"),
                        icon=KMVIZ_ICONS["cline"],
                        color=None
                    ),
                ])
            ]),
            make_accordion_items("Grid", [
                dmc.Group([
                    dmc.Switch(
                        id=pid("showgrid"),
                        size="lg",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    ),
                    make_nb_input(
                        pid("gridwidth"),
                        "Width",
                        (0, 1, None, 1),
                        icon=icons("width", rotate=1)
                    ),
                    make_select_input(
                        pid("griddash"),
                        "Dash",
                        data=make_select_data([
                            "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
                        ]),
                        icon=icons("dash")
                    ),
                    make_hover_color_picker(pid("gridcolor"), icon=KMVIZ_ICONS["cline"], color=None),
                ])
            ]),
            make_accordion_items("Tick Labels", [
                dmc.Group([
                    dmc.Switch(
                        id=pid("showticklabels"),
                        onLabel="ON",
                        offLabel="OFF",
                        size="lg",
                        checked=True
                    ),
                    dmc.Switch(
                        id=pid("automargin"),
                        onLabel="Automargin",
                        offLabel="Automargin",
                        size="lg",
                        checked=True
                    ),
                ]),
                dmc.Group([
                    make_nb_input(
                        pid("tickangle"),
                        "Angle",
                        (-180, 1, 180, 0),
                        icon=icons("angle")
                    ),
                    make_select_input(
                        pid("ticklabelposition"),
                        "Position",
                        data=make_select_data([
                            "outside", "inside", "outside top", "inside top",
                            "outside left", "inside left", "outside right", "inside right",
                            "outside bottom", "inside bottom"
                        ]),
                        icon=icons("pos")
                    ),
                    make_nb_input(
                        pid("tickfont_size"),
                        "Size",
                        (0, 1, 100, 14),
                        "Size",
                        icon=icons("font_size")
                    ),
                    make_font_input(
                        pid("tickfont_family"),
                        "Font",
                    ),
                    make_hover_color_picker(pid("tickfont_color"), icon=KMVIZ_ICONS["ctext"], color=None)
                ])
            ]),
            make_accordion_items("Tick Markers", [
                dmc.Group([
                    dmc.SegmentedControl(
                        data=make_select_data(["inside", "outside", "hide"], True),
                        fullWidth=True,
                        id=pid("ticks"),
                        size="xs",
                        value="hide",
                        color="#1C7ED6"
                    ),
                    make_nb_input(
                        pid("ticklen"),
                        "Length",
                        (0, 1, 100, 1),
                        icon=icons("width", rotate=1)
                    ),
                    make_nb_input(
                        pid("tickwidth"),
                        "Width",
                        (0, 1, 100, 1),
                        icon=icons("width")
                    ),
                    make_nb_input(
                        pid("nticks"),
                        "Max",
                        (0, 1, 1000, 10),
                        icon=icons("nindex")
                    ),
                    make_hover_color_picker(pid("tickcolor"), icon=KMVIZ_ICONS["cline"], color=None)
                ])
            ]),
        ])
    ])
    return res

def make_axis_callbacks(factory, ax, figure_id):
    pid = factory
    @callback(
        Output(figure_id, "figure"),
        inputs=dict(inputs=(
            State(pid("axis-index"), "value"),
            Input("kmviz-auto-apply", "checked"),
            Input(figure_id, "figure"),
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
        if ctx.triggered_id == figure_id and not inputs[1]:
            return no_update

        skip = set(["axis-index", figure_id, "kmviz-auto-apply"])

        if ax == "x":
            n = "xaxis" if inputs[0] == 0 else f"xaxis{inputs[0]+1}"
            if ctx.triggered_id == figure_id:
                return patch_figure_all(ctx, ["layout", n], skip)
            else:
                return patch_figure(ctx, ["layout", n])
        elif ax == "y":
            n = "yaxis" if inputs[0] == 0 else f"yaxis{inputs[0]+1}"
            if ctx.triggered_id == figure_id:
                return patch_figure_all(ctx, ["layout", n], skip)
            else:
                return patch_figure(ctx, ["layout", n])
        return no_update

def make_axes(factory):
    pid = factory.child("rangeslider")

    res = html.Div([
        dmc.Space(h=10),
        dmc.Grid([
            dmc.Col(make_axis(factory.child("xaxis"), "x"), span=6),
            dmc.Col(make_axis(factory.child("yaxis"), "y"), span=6),
        ]),
        make_accordion([
            make_accordion_items("Range slider", [
                dmc.Group([
                    dmc.Switch(
                        id=pid("rangeslider_visible"),
                        size="lg",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    ),
                    make_nb_input(
                        pid("rangeslider_borderwidth"),
                        "Width",
                        (0, 1, None, 1),
                        icon=icons("cline"),
                    ),
                    make_nb_input(
                        pid("rangeslider_thickness"),
                        "Thickness",
                        (0.0, 0.01, 1, 0.1),
                        2,
                        icon=icons("floating"),
                    ),
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
                    make_hover_color_picker(
                        pid("rangeslider_bordercolor"),
                        "Border color",
                        icon=KMVIZ_ICONS["cline"],
                        color=None
                    ),
                    make_hover_color_picker(
                        pid("rangeslider_bgcolor"),
                        "Background color",
                        icon=KMVIZ_ICONS["cback"],
                        color=None
                    )
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

    preset_select = make_select_input(
        pid.sid("select-preset"),
        None,
        placeholder="Select preset",
        clearable=True,
        icon=icons("preset"),
        style={"width": "170px"}
    )

    trace_type = make_select_input(
        pid.child("trace")("type"),
        None,
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
        searchable=True,
        icon=icons("plot"),
        style={"width": "170px"},
    )

    res =  html.Div([
        dcc.Graph(
            figure=blank_figure(),
            id=pid.sid("figure"),
            responsive=True,
            mathjax=True,
            style = {"margin-left": "auto", "margin-right": "auto", "height":"70vh", "width":"90%"},
            config={'modeBarButtonsToAdd':['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]}
        ),
        dmc.Tabs([
            dmc.TabsList([
                dmc.Tab("Trace", value="trace", disabled=False, id=pid.sid("trace-tab")),
                dmc.Tab("Title", value="title", disabled=False, id=pid.sid("title-tab")),
                dmc.Tab("Axes", value="axes", disabled=False, id=pid.sid("axes-tab")),
                dmc.Tab("Legend", value="legend", disabled=False, id=pid.sid("legend-tab")),
                dmc.Tab("Colorbar", value="colorbar", disabled=False, id=pid.sid("colobar-tab")),
                dmc.Tab("Shape", value="shape", disabled=False, id=pid.sid("shape-tab")),
                preset_select,
                dmc.ActionIcon(
                    DashIconify(icon="lucide:filter-x", width=20),
                    id=pid.sid("rmf"),
                    variant="filled",
                    style = {"margin-left": "auto", "margin-right": 0},
                    color = "#1C7ED6"
                ),
            ]),
            dmc.TabsPanel(
                make_trace(pid.child("trace")), value="trace"),
            dmc.TabsPanel(
                make_plot_title(pid.child("title")), value="title"),
            dmc.TabsPanel(
                make_axes(pid.child("axes")), value="axes"),
            dmc.TabsPanel(
                make_plot_legend(pid.child("legend")), value="legend"),
            dmc.TabsPanel(
                make_color_legend(pid.child("colorbar")), value="colorbar"),
            dmc.TabsPanel(
                make_plot_shape(pid.child("shape")), value="shape")

        ], value="trace")
    ])

    return res

def make_plot_callbacks(factory):
    pid = factory
    figure_id = pid.sid("figure")
    make_plot_title_callbacks(pid.child("title"), figure_id),
    make_plot_legend_callbacks(pid.child("legend"), figure_id)
    make_color_legend_callbacks(pid.child("colorbar"), figure_id)
    make_axes_callbacks(pid.child("axes"), figure_id)
    make_plot_shape_callbacks(pid.child("shape"), figure_id)



