from dash import Patch
import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, State, html, callback

from kmviz.core.log import kmv_info
from kmviz.core.provider.options import ProviderOption, RangeOption

from kmviz.ui import state

from kmviz.ui.utils import make_select_data
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.store import ksfr

kof = kf.child("option")
kcf = kf.child("config")

def make_range_option(opt: RangeOption, id):
    return html.Div([
        dmc.Text(opt.name, size="sm", weight=450, align="center"),
        dmc.Slider(
            id=id,
            min=opt.min,
            max=opt.max,
            step=opt.step,
            value=opt.value if opt.value else opt.default,
            updatemode="mouseup",
            precision=2,
        )
    ])

def make_user_option(opt: ProviderOption, id):
    if isinstance(opt, RangeOption):
        return make_range_option(opt, id)
    return None

def create_option_callback(provider_name, opt_name):
    def update(value):
        patch = Patch()
        patch[provider_name][opt_name] = value
        return patch
    return update

def make_options_callbacks():
    for provider_name, provider in state.kmstate.providers.all().items():
        for opt_name in provider.options:
            callback(
                Input(kof(f"{provider_name}-{opt_name}"), "value"),
                Output(ksfr("provider-options"), "data"),
                prevent_initial_callbacks=True
            )(create_option_callback(provider_name, opt_name))

def make_provider_config(provider_name):
    options = state.kmstate.providers.get(provider_name).options

    children = []

    for opt in options.values():
        children.append(make_user_option(opt, id=kof(f"{provider_name}-{opt.name}")))

    return html.Div(
        id=kcf(f"{provider_name}-div"),
        children=children,
        style={ "display": "none" }
    )

def make_config():
    provider_names = state.kmstate.providers.list()

    res = html.Div([
        dmc.Divider(size="sm", color="gray", label="CONFIGURATION", labelPosition="center"),
        dmc.Select(
            id=kf("select-provider-config"),
            clearable=True
        ),
        *[make_provider_config(name) for name in provider_names]
    ])

    return res

def make_config_callbacks():
    @callback(
        Input(kf("select-provider-config"), "value"),
        State(kcf.all, "id"),
        Output(kcf.all, "style"),
        prevent_initial_callbacks=True,
    )
    def show_provider_config(provider_name, idx):
        styles = [{"display": "none"} for _ in range(len(idx))]

        if not provider_name:
            return styles

        for index, id in enumerate(idx):
            if id["index"] == f"{provider_name}-div":
                styles[index]["display"] = "inline"
                return styles

    make_options_callbacks()




