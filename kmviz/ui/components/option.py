from dash import Patch
import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, State, html, callback

from kmviz.core.log import kmv_info
from kmviz.core.provider.options import ProviderOption, RangeOption, TextOption, NumericOption, ChoiceOption, MultiChoiceOption

from kmviz.ui.utils import make_select_data

from dash_iconify import DashIconify

def make_range_option(opt: RangeOption, id):
    v = opt.value if opt.value else opt.default
    text_id = id["type"] + "-" + id["index"] + "-" + opt.name
    return html.Div([
        dmc.Text(f"{opt.name} = {v}", size="sm", fw=450, ta="center", id=text_id),
        dmc.Slider(
            id=id,
            min=opt.min,
            max=opt.max,
            step=opt.step,
            value=opt.value if opt.value else opt.default,
            updatemode="mouseup",
            precision=2,
            className="kmviz-dmc-user-slider",
            marks=[
                {"value": opt.min, "label": str(round(opt.min, 2))},
                {"value": opt.max, "label": str(round(opt.max, 2))},
            ],
            size="sm"
        ),
        dmc.Space(h=13)
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
        className="kmviz-dmc-user-number-input",
        classNames={"root": "kmviz-dmc-numeric-input-root"},
    )

def make_choice_option(opt: ChoiceOption, id):
    return dmc.Select(
        id=id,
        label=opt.name,
        data=make_select_data(opt.choices),
        value=opt.value if opt.value else opt.default,
        className="kmviz-dmc-user-select",
        clearable=True,
        searchable=True,
        classNames={"root": "kmviz-dmc-select-input-root"},
    )

def make_multichoice_option(opt: MultiChoiceOption, id):
    return dmc.MultiSelect(
        id=id,
        label=opt.name,
        data=make_select_data(opt.choices),
        value=opt.value if opt.value else opt.default,
        className="kmviz-dmc-user-multi-select",
        clearable=True,
        searchable=True,
        classNames={"root": "kmviz-dmc-select-input-root"},
        size="xs"
    )

def make_text_option(opt: TextOption, id):
    return dmc.TextInput(
        id=id,
        label=opt.name,
        value=opt.value if opt.value else opt.default,
        placeholder=opt.placeholder,
        className="kmviz-dmc-user-text-input",
        classNames={"root": "kmviz-dmc-text-input-root"},
        size="xs"
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




