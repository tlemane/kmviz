from dash import Patch
import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, State, html, callback

from kmviz.core.log import kmv_info
from kmviz.core.provider.options import ProviderOption, RangeOption, TextOption, NumericOption, ChoiceOption, MultiChoiceOption

from kmviz.ui import state

from kmviz.ui.utils import make_select_data
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.store import ksfr

from dash_iconify import DashIconify
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
            className="kmviz-dmc-slider"
        )
    ])

def make_numeric_option(opt: NumericOption, id):
    return dmc.NumberInput(
        id=id,
        label=opt.name,
        min=opt.min,
        step=opt.step,
        max=opt.max,
        value=opt.value if opt.value else opt.default,
        precision=2,
        className="kmviz-dmc-number-input",
    )

def make_choice_option(opt: ChoiceOption, id):
    return dmc.Select(
        id=id,
        label=opt.name,
        data=make_select_data(opt.choices),
        value=opt.value if opt.value else opt.default,
        className="kmviz-dmc-select",
        clearable=True,
        searchable=True
    )

def make_multichoice_option(opt: MultiChoiceOption, id):
    return dmc.MultiSelect(
        id=id,
        label=opt.name,
        data=make_select_data(opt.choices),
        value=opt.value if opt.value else opt.default,
        className="kmviz-dmc-multi-select",
        clearable=True,
        searchable=True
    )

def make_text_option(opt: TextOption, id):
    return dmc.TextInput(
        id=id,
        label=opt.name,
        value=opt.value if opt.value else opt.dsefault,
        placeholder=opt.placeholder,
        className="kmviz-dmc-text-input"
    )

def make_user_option(opt: ProviderOption, id):
    if isinstance(opt, RangeOption):
        return make_range_option(opt, id)
    elif isinstance(opt, NumericOption):
        return make_numeric_option(opt, id)
    elif isinstance(opt, ChoiceOption):
        return make_choice_option(opt, id)
    elif isinstance(opt, MultiChoiceOption):
        return make_multichoice_option(opt, id)
    elif isinstance(opt, TextOption):
        return make_text_option(opt, id)
    return None

def create_option_callback(provider_name, opt_name):
    def update(value):
        patch = Patch()
        patch[provider_name][opt_name] = value
        return patch
    return update

def make_callback(name, opt_name, input_id, output_id):
    return callback(
        Input(input_id, "value"),
        Output(output_id, "data"),
        prevent_initial_callbacks=True
    )(create_option_callback(name, opt_name))

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
            clearable=True,
            icon=DashIconify(icon="mynaui:config")
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




