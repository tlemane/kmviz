from dash_extensions.enrich import no_update
from dash import Patch
from kmviz.ui.utils import patch_value, patch_value_id
from kmviz.ui.components.factory import dmc_new

def color_to_string(color):
    return color

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

def apply_presets(presets: dict, params: dict, priority: bool=True):
    if not presets:
        return params

    for k in list(presets.keys()):
        if presets[k] is None:
            del presets[k]

    if priority:
        return {**params, **presets}
    else:
        for k, v in params.items():
            if k in presets and v is not None:
                presets[k] = v
        return {**params, **presets}

def apply_legend_and_title_presets(fig, presets):
    title = {k: v for k, v in presets.title.model_dump().items() if v is not None}
    legend = {k: v for k, v in presets.legend.model_dump().items() if v is not None}

    if len(title):
        fig.update_layout(**title)

    if len(legend):
        fig.update_layout(**legend)

