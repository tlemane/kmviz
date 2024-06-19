from typing import List, Dict
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

def prevent_update_on_none(*values):
    if any(value is None for value in values):
        raise PreventUpdate()

def prevent_update_on_empty(*values):
    prevent_update_on_none(*values)
    if any(not len(value) for value in values):
        raise PreventUpdate()

def make_select_data(values: List[str], cap=False) -> Dict[str, str]:
    if cap:
        return [{ "label": x.capitalize(), "value": x } for x in values]
    return [{ "label": x, "value": x } for x in values]

KMVIZ_ICONS = dict(
    font_size = "file-icons:font-outline",
    family = "radix-icons:font-family",
    index = "iconoir:db",
    table = "material-symbols:table",
    map = "fluent-mdl2:world",
    plot = "carbon:qq-plot",
    dna = "mdi:dna",
    help = "material-symbols:help-outline",
    integer = "carbon:string-integer",
    floating = "mdi:decimal-comma",
    nindex = "tabler:number",
    text = "fluent-mdl2:text-field",
    multi = "fluent:multiselect-ltr-16-regular",
    single = "vaadin:select",
    width = "material-symbols-light:width",
    axis = "carbon:x-axis",
    cline = "material-symbols:border-color-rounded",
    cback = "material-symbols:format-color-fill-rounded",
    ctext = "material-symbols:format-color-text",
    dash = "ant-design:dash-outlined",
    angle = "tabler:angle",
    pos = "ep:position",
    indent = "bi:indent",
    X = "tabler:square-letter-x-filled",
    Y = "tabler:square-letter-y-filled",
    preset = "simple-icons:blueprint",
    style = "logos:stylefmt",
    picker = "mage:color-picker",
    json = "bi:filetype-json",
    autoff = "ic:outline-auto-fix-off",
    auton = "ic:outline-auto-fix-high"
)

def icons(name, **kwargs):
    return DashIconify(icon=KMVIZ_ICONS[name], **kwargs)

