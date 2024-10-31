from dash_extensions.enrich import html, dcc
import dash_mantine_components as dmc
import dash_ag_grid as dag
from typing import Dict, Any, Union, List, Optional
from kmviz.ui.utils import icons
import dash_bootstrap_components as dbc

import dash_daq as daq
IDType = Union[str, Dict[str, Any]]

from dash_mantine_components import __version__ as dmc_version

dmc_old = dmc_version == "0.12.1"
dmc_new = not dmc_old

def classname(base: str, idd: Optional[IDType], kwargs: Dict[str, Any]) -> str:
    if idd is None:
        sid = ""
    else:
        sid = idd if isinstance(idd, str) else f"{idd['type']}-{idd['index']}"

    c = f"{base} {sid}"
    if kwargs and "className" in kwargs:
        c += f" {kwargs['className']}"
    return c

def patch_dmc_value(old, new, d):
    if dmc_new:
        return
    if old in d:
        if not new:
            del d[old]
        else:
            tmp = d[old]
            del d[old]
            d[new] = tmp

def patch_dmc(kwargs: dict):
    patch_dmc_value("leftSection", "icon", kwargs)
    patch_dmc_value("decimalScale", "precision", kwargs)
    patch_dmc_value("gap", "spacing", kwargs)

def forward(kwargs: dict):
    if kwargs and "className" in kwargs:
        del kwargs["className"]

    if dmc_old:
        patch_dmc(kwargs)
    return kwargs

def dmc_select_version(old, new):
    if dmc_version == "0.12.1":
        return old
    return new

km_color = "#1C7ED6"
kshow = {"display": "inline"}
khide = {"display": "none"}

class ComponentFactory:

    _cls_prefix = "kmviz"
    _button = f"{_cls_prefix}-button"
    _select = f"{_cls_prefix}-select"
    _multi = f"{_cls_prefix}-multi"
    _slider = f"{_cls_prefix}-slider"
    _switch = f"{_cls_prefix}-switch"
    _number = f"{_cls_prefix}-number"
    _json = f"{_cls_prefix}-json"
    _text = f"{_cls_prefix}-text"
    _area = f"{_cls_prefix}-area"
    _color = f"{_cls_prefix}-color"

    _tabs = f"{_cls_prefix}-tabs"
    _tabs_list = f"{_cls_prefix}-tabs-list"
    _tabs_tab = f"{_cls_prefix}-tabs-tab"
    _tabs_panel = f"{_cls_prefix}-tabs-panel"

    _upload = f"{_cls_prefix}-upload"

    _group = f"{_cls_prefix}-group"

    _div = f"{_cls_prefix}-div"

    _h1 = f"{_cls_prefix}-h1"
    _h2 = f"{_cls_prefix}-h2"
    _h3 = f"{_cls_prefix}-h3"
    _h4 = f"{_cls_prefix}-h4"

    _center = f"{_cls_prefix}-center"
    _divider = f"{_cls_prefix}-divider"


    _action = f"{_cls_prefix}-action"
    _segmented = f"{_cls_prefix}-segmented"

    _ag_grid = f"{_cls_prefix}-ag-grid"

    @staticmethod
    def _make_select_data(data: Union[List[str], List[Dict[str, str]]]):
        if data and isinstance(data[0], str):
            return [{ "label": value, "value": value } for value in data]
        return data

    @classmethod
    def button(cls, id: IDType, children: Any, **kwargs) -> dmc.Button:
        patch_dmc_value("leftSection", "leftIcon", kwargs)
        return dmc.Button(
            children,
            id=id,
            className=classname(cls._button, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def action(cls, id: IDType, icon: Any, **kwargs) -> dmc.ActionIcon:
        return dmc.ActionIcon(
            icon,
            id=id,
            className=classname(cls._action, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def color(cls, id: IDType, **kwargs):
        if dmc_old:
            return cls._old_color(id, **kwargs)
        else:
            return dmc.ColorInput(
                id=id,
                className=classname(cls._color, id, kwargs),
                **forward(kwargs)
            )

    @classmethod
    def _old_color(cls, id: IDType, **kwargs):
        format = None if "noTranspa" in kwargs else "rgba"
        return html.Div([
            dmc.Badge(kwargs["label"], size="sm", id=f"{str(id)}-target", className=classname(cls._color, id, kwargs)),
            dbc.Popover(
                dmc.ColorPicker(id=id, value=kwargs["value"] if "value" in kwargs else None, format=format),
                target=f"{str(id)}-target",
                trigger="hover"
            )
        ])

    @classmethod
    def select(cls, id: IDType, data: Union[List[str], List[Dict[str, str]]], **kwargs) -> dmc.Select:
        return dmc.Select(
            id=id,
            data=cls._make_select_data(data),
            className=classname(cls._select, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def multi(cls, id: IDType, data: Union[List[str], List[Dict[str, str]]], **kwargs) -> dmc.MultiSelect:
        return dmc.MultiSelect(
            id=id,
            data=cls._make_select_data(data),
            className=classname(cls._multi, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def slider(cls, id: IDType, **kwargs) -> dmc.Slider:
        return dmc.Slider(
            id=id,
            className=classname(cls._slider, id, kwargs)
            **forward(kwargs)
        )

    @classmethod
    def switch(cls, id: IDType, **kwargs) -> dmc.Switch:
        return dmc.Switch(
            id=id,
            className=classname(cls._switch, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def number(cls, id: IDType, **kwargs) -> dmc.NumberInput:
        return dmc.NumberInput(
            id=id,
            className=classname(cls._number, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def segmented(cls, id: IDType, data: Union[List[str], List[Dict[str, str]]], **kwargs) -> dmc.SegmentedControl:
        return dmc.SegmentedControl(
            id=id,
            data=cls._make_select_data(data),
            className=classname(cls._segmented, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def json(cls, id: IDType, **kwargs) -> dmc.JsonInput:
        return dmc.JsonInput(
            id=id,
            className=classname(cls._json, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def text(cls, id: IDType, **kwargs) -> dmc.TextInput:
        return dmc.TextInput(
            id=id,
            className=classname(cls._text, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def area(cls, id: IDType, **kwargs) -> dmc.Textarea:
        return dmc.Textarea(
            id=id,
            className=classname(cls._area, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def group(cls, id: IDType, *components, **kwargs) -> dmc.Group:
        return dmc.Group(
            components,
            id=id,
            className=classname(cls._group, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def font(cls, id: IDType, **kwargs) -> dmc.Select:
        data = [
            "Arial", "Balto", "Courier New", "Droid Sans",
            "Droid Serif", "Droid Sans Mono", "Gravitas One",
            "Old Standard TT", "Open Sans", "Overpass",
            "PT Sans Narrow", "Raleway", "Times New Roman"
        ]
        return cls.select(id, data=data, value="Arial", leftSection=icons("family"), **kwargs)

    @classmethod
    def sseqscale(cls, id: IDType, **kwargs) -> dmc.Select:
        data = [
            'Brwnyl', 'Agsunset', 'Sunsetdark', 'Magenta', 'Sunset',
            'Purpor', 'Purp', 'Tealgrn', 'Teal', 'Bluyl', 'Aggrnyl',
            'Emrld', 'Darkmint', 'Blugrn', 'Mint', 'Pinkyl',
            'Peach', 'Oryel', 'Redor', 'Burgyl', 'Burg',
            'tempo', 'amp', 'speed', 'matter', 'algae', 'dense', 'deep',
            'gray', 'ice', 'solar', 'haline', 'thermal', 'turbid', 'YlOrRd',
            'YlOrBr', 'YlGnBu', 'YlGn', 'Reds', 'RdPu', 'RdBu', 'Purples',
            'PuRd', 'PuBuGn', 'PuBu', 'Oranges', 'OrRd', 'Greys', 'Greens',
            'GnBu', 'BuPu', 'BuGn', 'Blues', 'Rainbow', 'Jet', 'Hot', 'Electric',
            'Bluered', 'Blackbody', 'Turbo', 'Plasma', 'Magma', 'Inferno',
            'Cividis', 'Viridis', 'Plotly3'
        ]
        return cls.select(id, data=data, leftSection=icons("picker"), **kwargs)

    @classmethod
    def sdivscale(cls, id: IDType, **kwargs) -> dmc.Select:
        data = [
            'Portland', 'Picnic', 'Earth', 'Tropic', 'Tealrose', 'Temps', 'Geyser',
            'Fall', 'Armyrose', 'oxy', 'curl', 'delta', 'balance',
            'Spectral', 'RdYlGn', 'RdYlBu', 'RdGy', 'RdBu', 'PuOr', 'PiYG',
            'PRGn', 'BrBG'
        ]
        return cls.select(id, data=data, leftSection=icons("picker"), **kwargs)

    @classmethod
    def scycscale(cls, id: IDType, **kwargs) -> dmc.Select:
        data = ['mygbm', 'mrybm', 'HSV', 'Phase', 'Edge', 'IceFire', 'Twilight']
        return cls.select(id, data=data, leftSection=icons("picker"), **kwargs)

    @classmethod
    def div(cls, id: IDType, *children, **kwargs) -> html.Div:
        return html.Div(
            children=children,
            id=id,
            className=classname(cls._div, id, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def h1(cls, text: str, id: Optional[IDType]=None, **kwargs) -> html.H1:
        return html.H1(text, className=classname(cls._h1, id, kwargs), **forward(kwargs))

    @classmethod
    def h2(cls, text: str, id: Optional[IDType]=None, **kwargs) -> html.H2:
        return html.H2(text, className=classname(cls._h2, id, kwargs), **forward(kwargs))

    @classmethod
    def h3(cls, text: str, id: Optional[IDType]=None, **kwargs) -> html.H3:
        return html.H3(text, className=classname(cls._h3, id, kwargs), **forward(kwargs))

    @classmethod
    def h4(cls, text: str, id: Optional[IDType]=None, **kwargs) -> html.H4:
        return html.H4(text, className=classname(cls._h4, id, kwargs), **forward(kwargs))

    @classmethod
    def divider(cls, **kwargs) -> dmc.Divider:
        return dmc.Divider(
            className=classname(cls._divider, None, kwargs),
            **forward(kwargs)
        )

    @classmethod
    def upload(cls, id: IDType, content: Any) -> dcc.Upload:
        return dcc.Upload(
            content,
            id=id,
            className=classname(cls._upload, id, {})
        )

    @classmethod
    def store(cls, id: IDType, data: Optional[Any]=None, **kwargs) -> dcc.Store:
        return dcc.Store(id=id, data=data, **kwargs)

    @classmethod
    def tabs(cls, id: IDType, *content: Any, value: Optional[str], **kwargs) -> dmc.Tabs:
        return dmc.Tabs(content, value=value, id=id, className=classname(cls._tabs, id, kwargs), **forward(kwargs))

    @classmethod
    def tabs_list(cls, id: IDType, *content: Any, **kwargs) -> dmc.TabsList:
        return dmc.TabsList(content, id=id, className=classname(cls._tabs_list, id, kwargs), **forward(kwargs))

    @classmethod
    def tabs_tab(cls, id: IDType, content: Any, value: str, **kwargs):# -> dmc.TabsTab:
        if dmc_old:
            return dmc.Tab(content, value=value, id=id, className=classname(cls._tabs_tab, id, kwargs), **forward(kwargs))
        else:
            return dmc.TabsTab(content, value=value, id=id, className=classname(cls._tabs_tab, id, kwargs), **forward(kwargs))

    @classmethod
    def tabs_panel(cls, id: IDType, content: Any, value: str, **kwargs):#! -> dmc.TabsTab:
        return dmc.TabsPanel(content, value=value, id=id, className=classname(cls._tabs_panel, id, kwargs), **forward(kwargs))

    @classmethod
    def ag_grid(cls, id: IDType,
                grid_opt: Dict[str, Any]={},
                col_def: Dict[str, Any]={},
                export: Dict[str, Any]={}, **kwargs) -> dag.AgGrid:

        #c = "ag-theme-balham" + " " + classname(cls._ag_grid, id, kwargs)
        c = "ag-theme-balham"

        _default = {
            "columnSize": "autoSize",
            "className": c
        }

        _default_col_def = {
            "filter": True,
            "sortable": True,
            "floatingFilter": True
        }

        _default_grid_opt = {
            "suppressMenuHide": False,
            "animateRows": False,
            "pagination": True,
            "loadingOverlayComponent": "CustomLoadingOverlay",
            "loadingOverlayComponentParams": {
                "loadingMessage": "Waiting for results..."
            },
            "rowSelection": "single",
            "enableCellTextSelection": True,
            "ensureDomOrder": True
        }

        _default_export = {
            "fileName": "data.tsv",
            "columnSeparator": "\t"
        }

        return dag.AgGrid(
            id=id,
            defaultColDef={**_default_col_def, **col_def },
            dashGridOptions={**_default_grid_opt, **grid_opt},
            csvExportParams={**_default_export, **export},
            **{**_default, **forward(kwargs)}
        )

