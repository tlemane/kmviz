import plotly.express as px
from kmviz.ui.utils import prevent_update_on_empty, prevent_update_on_none, PreventUpdate

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

px_histo_options = {
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
    "animation_frame",
    "animation_group",
    "category_orders",
    "labels",
    "color_discrete_sequence",
    "color_discrete_map",
    "pattern_shape_sequence",
    "pattern_shape_map",
    "opacity",
    "orientation",
    "barmode",
    "log_x",
    "log_y",
    "range_x",
    "histfunc",
    "histnorm",
    "cumulative",
    "nbins",
    "range_y",
    "text_auto",
    "title",
    "template",
    "width",
    "height",
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
    "Box": px_box_options,
    "Histogram": px_histo_options
}

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

    if ptype == "Histogram":
        return px.histogram(df, x=X, y=Y, hover_name="ID", **params)

def fix_px_params(params, ptype):
    for k in list(params):
        if k not in px_options[ptype]:
            del params[k]
    return params

def to_bool(value):
    return True if value == "True" else False

def select_cscale(scales):
    scale = None
    if any(scales):
        next(s for s in scales if s is not None)
    return scale

def valid_input(ptype, X, Y, Z):

    if not ptype:
        raise PreventUpdate

    if ptype not in {"Parallel coordinates", "Parallel categories", "Pie", "Scatter matrix"}:
        prevent_update_on_empty(X, Y)

    if ptype in {"Density heatmap", "Density contour"}:
        prevent_update_on_empty(Z)


