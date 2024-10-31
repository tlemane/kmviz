
from pydantic import BaseModel
from typing import Literal, Optional, Annotated, Union, List, Dict, Any
from annotated_types import Ge, Le
from dash_extensions.enrich import no_update

class title_presets(BaseModel):
    title_text: Optional[str]=None
    title_font_size: Optional[int]=None
    title_font_familiy: Optional[Literal["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT", "Open Sans", "Overpass", "PT Sans Narrow", "Raleway", "Times New Roman"]]=None
    title_font_color: Optional[str]=None

    title_xanchor: Optional[Literal["auto", "left", "center", "right"]]=None
    title_xref: Optional[Literal["container", "paper"]]=None
    title_x: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None

    title_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]]=None
    title_yref: Optional[Literal["container", "paper"]]=None
    title_y: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None

class legend_presets(BaseModel):
    legend_title_text: Optional[str]=None
    legend_title_font_size: Optional[int]=None
    legend_title_font_familiy: Optional[Literal["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT", "Open Sans", "Overpass", "PT Sans Narrow", "Raleway", "Times New Roman"]]=None
    legend_title_font_color: Optional[str]=None

    legend_xanchor: Optional[Literal["auto", "left", "center", "right"]]=None
    legend_xref: Optional[Literal["container", "paper"]]=None
    legend_x: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    legend_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]]=None
    legend_yref: Optional[Literal["container", "paper"]]=None
    legend_y: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None

    legend_indentation: Annotated[Optional[int], Ge(-15), Le(100)]=None
    legend_orientation: Optional[Literal["v", "h"]]=None

    legend_font_size: Optional[int]=None
    legend_font_familiy: Optional[Literal["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT", "Open Sans", "Overpass", "PT Sans Narrow", "Raleway", "Times New Roman"]]=None
    legend_font_color: Optional[str]=None

    legend_borderwidth: Annotated[Optional[int], Ge(0), Le(100)]=None
    legend_bordercolor: Optional[str]=None
    legend_bgcolor: Optional[str]=None

class map_presets(BaseModel):
    color: Optional[str]=None
    size: Optional[str]=None
    text: Optional[str]=None
    symbol: Optional[str]=None
    animation_frame: Optional[str]=None
    animation_group: Optional[str]=None
    template: Optional[str]=None
    projection: Optional[str]=None
    color_seq_continuous_scale: Optional[str]=None
    color_div_continuous_scale: Optional[str]=None
    color_cyc_continuous_scale: Optional[str]=None
    color_continuous_midpoint: Optional[Union[int, float]]=None
    opacity: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    size_max: Annotated[Optional[int], Ge(0), Le(50)]=None
    color_discrete_map: Optional[Dict[Any, str]]=None
    symbol_map: Optional[Dict[Any, str]]=None
    color_discrete_sequence: Optional[List[str]]=None
    symbol_sequence: Optional[List[str]]=None

    title: Optional[title_presets]=title_presets()
    legend: Optional[legend_presets]=legend_presets()

class plot_presets(BaseModel):
    type: str

    X: Optional[List[str]]=None
    Y: Optional[List[str]]=None
    Z: Optional[List[str]]=None
    color: Optional[str]=None
    size: Optional[str]=None
    text: Optional[str]=None
    symbol: Optional[str]=None
    pattern_shape: Optional[str]=None
    base: Optional[str]=None
    line_dash: Optional[str]=None
    line_group: Optional[str]=None
    dimensions: Optional[List[str]]=None
    values: Optional[str]=None
    names: Optional[str]=None

    animation_frame: Optional[str]=None
    animation_group: Optional[str]=None
    template: Optional[str]=None

    color_seq_continuous_scale: Optional[str]=None
    color_div_continuous_scale: Optional[str]=None
    color_cyc_continuous_scale: Optional[str]=None
    color_continuous_midpoint: Optional[Union[int, float]]=None
    opacity: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    size_max: Annotated[Optional[int], Ge(0), Le(50)]=None

    color_discrete_map: Optional[Dict[Any, str]]=None
    symbol_map: Optional[Dict[Any, str]]=None
    color_discrete_sequence: Optional[List[str]]=None
    symbol_sequence: Optional[List[str]]=None

    pattern_shape_map: Optional[Dict[Any, str]]=None
    line_dash_map: Optional[Dict[Any, str]]=None
    pattern_shape_sequence: Optional[List[str]]=None
    line_dash_sequence: Optional[List[str]]=None

    trendline: Optional[Literal["ols", "lowess", "rolling", "expanding", "ewm"]]=None
    trendline_scope: Optional[Literal["trace", "overall"]]=None
    trendline_options: Optional[Dict[Any, str]]=None

    marginal_x: Optional[Literal["rug", "box", "violin", "histogram"]]=None
    marginal_y: Optional[Literal["rug", "box", "violin", "histogram"]]=None

    histfunc: Optional[Literal["count", "sum", "avg", "min", "max"]]=None
    histnorm: Optional[Literal["rug", "box", "violin", "histogram"]]=None
    nbins: Annotated[Optional[int], Ge(1), Le(1000)]=None

    facet_row: Optional[str]=None
    facet_col: Optional[str]=None
    facet_col_spacing: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    facet_row_spacing: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    facet_col_wrap: Annotated[Optional[int], Ge(0), Le(10)]=None

    title: Optional[title_presets]=title_presets()
    legend: Optional[legend_presets]=legend_presets()

class cpresets_defaults(BaseModel):
    map: Optional[str]=None
    plot: Optional[str]=None

class cpresets(BaseModel):
    priority: Optional[bool]=None
    map: Optional[Dict[str, map_presets]]=None
    plot: Optional[Dict[str, plot_presets]]=None
    defaults: Optional[cpresets_defaults]=cpresets_defaults()

def set_preset_values(ids: list, preset: dict) -> list:
    r = [no_update for _ in range(len(ids))]
    for index, id in enumerate(ids):
        if id["index"] in ("xselect", "yselect", "zselect"):
            id["index"] = id["index"][0].upper()
        if id["index"] in preset:
            r[index] = preset[id["index"]]
    return r

