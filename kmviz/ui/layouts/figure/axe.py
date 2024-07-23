from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color, dmc_old
from kmviz.ui.layouts.figure import patch_figure, patch_figure_all
from kmviz.ui.id_factory import IDFactory, kid
from kmviz.ui.utils import icons
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from typing import Any
from dash_extensions.enrich import callback, no_update, Input, State, Output, ctx


class AxeLayout:
    def __init__(self, v: str, factory: IDFactory, figure_id):
        self.v = v
        self.fid = figure_id
        self.f = factory.new(self.v)

    def _select_axe(self, if_x: Any, if_y: Any):
        return if_x if self.v == "x" else if_y

    def _title_panel(self):
        return cf.tabs_panel(
            self.f["title-panel"],
            [
                cf.group(
                    self.f["title-grp-1"],
                    cf.text(self.f("title_text"), label="Text", placeholder="<b>Title</b>", size="xs", value=None),
                    cf.number(self.f("title_font_size"), label="Font size", leftSection=icons("font_size"), min=0, max=100, value=None, step=1, placeholder="14", size="xs"),
                    cf.font(self.f("title_font_family"), label="Font", size="xs"),
                    cf.color(self.f("title_font_color"), label="Font color", size="xs", value="#000000"),
                    cf.number(self.f("title_standoff"), label="Standoff", leftSection=icons("floating"), min=0, max=None, step=0.01, value=None, decimalScale=2, size="xs"),
                )
            ],
            value="title"
        )

    def _line_panel(self):
        return cf.tabs_panel(
            self.f["line-panel"],
            [
                cf.group(
                    self.f["line-grp-1"],
                    cf.number(self.f("linewidth"), label="Width", min=0, max=100, step=1, value=None, size="xs", leftSection=icons("width", rotate=1)),
                    cf.select(self.f("type"), label="Type", data=["linear", "log", "date", "category", "multicategory"], size="xs", leftSection=icons("axis"), className="kmviz-figure-select"),
                    cf.select(self.f("mirror"), label="Mirror", data=["True", "False", "ticks", "allticks"], size="xs", value="False", leftSection=icons("single"), className="kmviz-figure-select"),
                    cf.color(self.f("linecolor"), label="Line color", size="xs"),
                    cf.segmented(self.f("side"), data=self._select_axe(["top", "bottom"], ["left", "right"]), value=self._select_axe("bottom", "left"), size="xs", color=km_color, className="kmviz-figure-segmented"),
                    cf.switch(self.f("visible"), size="lg", onLabel="ON", offLabel="OFF", checked=True, className="kmviz-figure-switch"),
                )
            ],
            value="line"
        )

    def _zero_panel(self):
        return cf.tabs_panel(
            self.f["zero-panel"],
            [
                cf.group(
                    self.f["zero-grp-1"],
                    cf.number(self.f("zerolinewidth"), label="Width", min=0, max=None, step=1, value=1, leftSection=icons("width", rotate=1), size="xs"),
                    cf.color(self.f("zerolinecolor"), label="Line color", size="xs"),
                    cf.switch(self.f("zeroline"), size="lg", onLabel="ON", offLabel="OFF", checked=True, className="kmviz-figure-switch"),
                )
            ],
            value="zeroline"
        )

    def _grid_panel(self):
        return cf.tabs_panel(
            self.f["grid-panel"],
            [
                cf.group(
                    self.f["grid-grp-1"],
                    cf.number(self.f("gridwidth"), label="Width", min=0, max=None, step=1, value=None, leftSection=icons("width", rotate=1), size="xs"),
                    cf.select(self.f("griddash"), label="Style", data=["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"], size="xs", value="solid", leftSection=icons("dash"), className="kmviz-figure-select"),
                    cf.color(self.f("gridcolor"), label="Grid color", size="xs"),
                    cf.switch(self.f("showgrid"), size="lg", onLabel="ON", offLabel="OFF", checked=True, className="kmviz-figure-switch"),
                )
            ],
            value="grid"
        )

    def _label_panel(self):
        return cf.tabs_panel(
            self.f["label-panel"],
            [
                cf.group(
                    self.f["label-grp-1"],

                    cf.number(self.f("tickangle"), label="Angle", min=-180, max=180, step=1, value=None, leftSection=icons("angle"), size="xs"),
                    cf.select(self.f("ticklabelposition"),
                              data=["outside", "inside", "outside top", "inside top", "outside left", "inside left", "outside right", "outside bottom", "inside bottom"],
                              size="xs", leftSection=icons("pos"), label="Position", className="kmviz-figure-select"),
                    cf.number(self.f("tickfont_size"), label="Font size", min=0, max=100, step=1, value=None, leftSection=icons("font_size"), size="xs"),
                    cf.font(self.f("tickfont_family"), label="Font", size="xs", className="kmviz-figure-select"),
                    cf.color(self.f("tickfont_color"), label="Label color", size="xs"),
                    cf.switch(self.f("showticklabels"), size="lg", onLabel="ON", offLabel="OFF", checked=True, className="kmviz-figure-switch"),
                    cf.switch(self.f("automargin"), size="lg", onLabel="Automargin", offLabel="Automargin", checked=True, className="kmviz-figure-switch"),

                )
            ],
            value="ticklabels"
        )

    def _marker_panel(self):
        return cf.tabs_panel(
            self.f["marker-panel"],
            [
                cf.group(
                    self.f["marker-grp-1"],

                    cf.number(self.f("ticklen"), label="Length", min=0, max=100, step=1, value=1, leftSection=icons("width", rotate=1), size="xs"),
                    cf.number(self.f("tickwidth"), label="Width", min=0, max=100, step=1, value=1, leftSection=icons("width"), size="xs"),
                    cf.number(self.f("nticks"), label="Max", min=0, max=10000, step=1, value=None, leftSection=icons("nindex"), size="xs"),
                    cf.color(self.f("tickcolor"), label="Tick color", size="xs"),
                    cf.segmented(self.f("ticks"), data=["inside", "outside", "hide"], value="hide", size="xs", color=km_color, className="kmviz-figure-segmented", fullWidth=True),
                )
            ],
            value="tickmarkers"
        )

    def layout(self):
        return cf.tabs(
            self.f["axe"],
            cf.tabs_list(
                self.f["axe-tabslist"],
                icons(self.v.upper(), color=km_color, width=30),
                cf.tabs_tab(self.f["title-tab"], "Title", value="title"),
                cf.tabs_tab(self.f["line-tab"], "Line", value="line"),
                cf.tabs_tab(self.f["zeroline-tab"], "Zeroline", value="zeroline"),
                cf.tabs_tab(self.f["grid-tab"], "Grid", value="grid"),
                cf.tabs_tab(self.f["tickslabels-tab"], "Tick Labels", value="ticklabels"),
                cf.tabs_tab(self.f["ticksmarkers-tab"], "Tick Markers", value="tickmarkers"),
                cf.number(self.f("axis-index"), min=0, max=20, step=1, value=0, leftSection=DashIconify(icon="tabler:number"), size="xs", style = {})#{"width": "75px", "height": "20px", "margin-top": "1px"}),
            ),
            self._title_panel(),
            self._line_panel(),
            self._zero_panel(),
            self._grid_panel(),
            self._label_panel(),
            self._marker_panel(),
            value=None,
            className="kmviz-fix-axes"
        )

    def callbacks(self):
        @callback(
            Output(self.fid, "figure"),
            inputs=dict(inputs=(
                State(self.f("axis-index"), "value"),
                Input(kid.kmviz("auto"), "checked"),
                Input(self.fid, "figure"),
                Input(self.f("title_text"), "value"),
                Input(self.f("title_font_size"), "value"),
                Input(self.f("title_font_color"), "value"),
                Input(self.f("title_font_family"), "value"),
                Input(self.f("title_standoff"), "value"),
                Input(self.f("visible"), "checked"),
                Input(self.f("type"), "value"),
                Input(self.f("side"), "value"),
                Input(self.f("linewidth"), "value"),
                Input(self.f("linecolor"), "value"),
                Input(self.f("mirror"), "value"),
                Input(self.f("showgrid"), "checked"),
                Input(self.f("griddash"), "value"),
                Input(self.f("gridwidth"), "value"),
                Input(self.f("gridcolor"), "value"),
                Input(self.f("showticklabels"), "checked"),
                Input(self.f("tickangle"), "value"),
                Input(self.f("ticklabelposition"), "value"),
                Input(self.f("tickfont_family"), "value"),
                Input(self.f("tickfont_size"), "value"),
                Input(self.f("tickfont_color"), "value"),
                Input(self.f("automargin"), "checked"),
                Input(self.f("ticks"), "value"),
                Input(self.f("ticklen"), "value"),
                Input(self.f("tickwidth"), "value"),
                Input(self.f("nticks"), "value"),
                Input(self.f("tickcolor"), "value"),
                Input(self.f("zeroline"), "checked"),
                Input(self.f("zerolinecolor"), "value"),
                Input(self.f("zerolinewidth"), "value"),
            )),
            prevent_initial_call=True,
        )
        def update_axis(inputs):
            if ctx.triggered_id == self.fid and not inputs[1]:
                return no_update

            skip = set([self.f("axis-index", True), self.fid, kid.kmviz("auto", True)])

            def make_patch(ax):
                n = f"{ax}axis" if inputs[0] == 0 else f"{ax}axis{inputs[0]+1}"
                if ctx.triggered_id == self.fid:
                    return patch_figure_all(ctx, ["layout", n], skip)
                else:
                    return patch_figure(ctx, ["layout", n])

            return make_patch(self.v)

class AxesLayout:
    def __init__(self, factory: IDFactory, figure_id):
        self.f = factory
        self.fid = figure_id
        self.x = AxeLayout("x", self.f, self.fid)
        self.y = AxeLayout("y", self.f, self.fid)

    def layout(self):
        if dmc_old:
            return cf.div(
                self.f["axes"],
                dmc.Grid([
                    dmc.Col(self.x.layout(), span=6),
                    dmc.Col(self.y.layout(), span=6),
                ])
            )
        else:
            return cf.div(
                self.f["axes"],
                dmc.Grid([
                    dmc.GridCol(self.x.layout(), span=6),
                    dmc.GridCol(self.y.layout(), span=6),
                ])
            )


    def callbacks(self):
        self.x.callbacks()
        self.y.callbacks()

