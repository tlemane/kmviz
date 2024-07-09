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
    v = opt.value if opt.value else opt.default
    text_id = id["type"] + "-" + id["index"] + "-" + opt.name
    return html.Div([
        dmc.Text(f"{opt.name} = {v}", size="sm", weight=450, align="center", id=text_id),
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

def create_range_text_callback(opt_name):
    def update(value):
        return [f"{opt_name} = {value}"]
    return update

def make_callback(name, opt_name, input_id, output_id):
    return callback(
        Input(input_id, "value"),
        Output(output_id, "data"),
        prevent_initial_call=True
    )(create_option_callback(name, opt_name))

def make_options_callbacks():
    for provider_name, provider in state.kmstate.providers.all().items():
        for opt_name in provider.options:
            if hasattr(provider.options[opt_name], "is_hidden"):
                continue
            callback(
                Input(kof(f"{provider_name}-{opt_name}"), "value"),
                Output(ksfr("provider-options"), "data"),
                prevent_initial_call=True
            )(create_option_callback(provider_name, opt_name))
            if isinstance(provider.options[opt_name], RangeOption):
                iid = kof(f"{provider_name}-{opt_name}")
                callback(
                    Input(iid, "value"),
                    Output(f"{iid['type']}-{iid['index']}-{opt_name}", "children")
                )(create_range_text_callback(opt_name))

def make_provider_config(provider_name):
    options = state.kmstate.providers.get(provider_name).options

    children = []

    if state.kmstate.providers.get(provider_name).has_visible_options:
        for opt in options.values():
            if opt.hidden:
                continue
            children.append(make_user_option(opt, id=kof(f"{provider_name}-{opt.name}")))

    return html.Div(
        id=kcf(f"{provider_name}-div"),
        children=children,
        style={"display": "inline" if provider_name == state.kmstate.defaults["configuration"] else "none"}
    )

def make_config():
    provider_names = state.kmstate.providers.list()

    if state.kmstate.defaults["configuration"]:
        data = make_select_data(state.kmstate.defaults["databases"])
        value = state.kmstate.defaults["configuration"]
    else:
        data = None
        value = None

    show_conf = True

    if state.kmstate.defaults["hide_db"]:
        provider_name = state.kmstate.defaults["databases"][0]
        show_conf = state.kmstate.providers.get(provider_name).has_visible_options
    else:
        show_conf = any(state.kmstate.providers.get(p).has_visible_options for p in provider_names)

    show_select = show_conf and not state.kmstate.defaults["hide_db"]

    res = html.Div([
        dmc.Divider(size="sm", color="gray", label="CONFIGURATION", labelPosition="center"),
        dmc.Select(
            id=kf("select-provider-config"),
            clearable=True,
            icon=DashIconify(icon="mynaui:config"),
            data=data,
            value=value,
            style = {"display": "inline" if show_select else "none" }
        ),
        *[make_provider_config(name) for name in provider_names]
    ], style = {"display": "inline" if show_conf else "none" })

    return res

def make_config_callbacks():
    @callback(
        Input(kf("select-provider-config"), "value"),
        State(kcf.all, "id"),
        Output(kcf.all, "style"),
        prevent_initial_call=True,
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




