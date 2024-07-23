from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color
from kmviz.ui.utils import icons
from kmviz.ui.id_factory import IDFactory, kid
from dash_extensions.enrich import Input, Output, no_update, callback, ctx
from kmviz.ui.layouts.figure import patch_figure, patch_figure_all
import dash_mantine_components as dmc

class LegendLayout:
    def __init__(self, factory: IDFactory, figure_id):
        self.f = factory
        self.fid = figure_id

    def _title_panel(self):
        return cf.tabs_panel(
            self.f["title-panel"],
            [
                cf.group(
                    self.f["title-grp-1"],
                    cf.text(self.f("legend_title_text"), label="Text", placeholder="<b>Title</b>", size="xs"),
                    cf.number(self.f("legend_title_font_size"), label="Font size", leftSection=icons("font_size"), min=0, max=100, value=None, step=1, placeholder="14", size="xs"),
                    cf.font(self.f("legend_title_font_family"), label="Font", size="xs"),
                    cf.select(self.f("legend_title_side"), data=["top", "left", "top left", "top center", "top right"], label="Position", value="top", size="xs", leftSection=icons("pos"), className="kmviz-figure-select"),
                    cf.color(self.f("legend_title_font_color"), label="Font color", size="xs", value="#000000"),
                )
            ],
            value="title"
        )

    def _position_panel(self):
        orient = [
            {"label": "vertical", "value": "v"},
            {"label": "horizontal", "value": "h"},
        ]
        return cf.tabs_panel(
            self.f["position-panel"],
            [
                cf.group(
                    self.f["position-grp-1"],
                    cf.select(self.f("legend_xanchor"), label="Anchor X", data=["auto", "left", "center", "right"], value="auto", leftSection=icons("single"), size="xs"),
                    cf.select(self.f("legend_xref"), label="Reference X", data=["container", "paper"], value="container", leftSection=icons("single"), size="xs"),
                    cf.number(self.f("legend_x"), label="x", min=0.0, max=1.0, step=0.01, value=0.9, startValue=0.9, placeholder="0.5", decimalScale=2, leftSection=icons("floating"), size="xs"),
                    cf.select(self.f("legend_yanchor"), label="Anchor Y", data=["auto", "top", "middle", "bottom"], value="auto", leftSection=icons("single"), size="xs"),
                    cf.select(self.f("legend_yref"), label="Reference Y", data=["container", "paper"], value="container", leftSection=icons("single"), size="xs"),
                    cf.number(self.f("legend_y"), label="y", min=0.0, max=1.0, step=0.01, value=None, startValue=0.9, placeholder="0.95", decimalScale=2, leftSection=icons("floating"), size="xs"),
                    cf.number(self.f("legend_indentation"), label="Identation", min=-15, max=100, step=1, value=0, leftSection=icons("indent"), size="xs"),
                    cf.segmented(self.f("legend_orientation"), data=orient, value="v", size="xs", className="kmviz-figure-segmented"),
                )
            ],
            value="position"
        )

    def _box_panel(self):
        return cf.tabs_panel(
            self.f["box-panel"],
            [
                cf.group(
                    self.f["box-grp-1"],
                    cf.number(self.f("legend_borderwidth"), label="Width", min=0, max=100, step=1, value=0, leftSection=icons("width", rotate=1), size="xs"),
                    cf.color(self.f("legend_bordercolor"), label="Border color", size="xs"),
                    cf.color(self.f("legend_bgcolor"), label="Bg color", size="xs"),
                )
            ],
            value="box"
        )

    def _entry_panel(self):
        return cf.tabs_panel(
            self.f["entry-panel"],
            [
                cf.group(
                    self.f["entry-grp-1"],
                    cf.font(self.f("legend_font_family"), label="Font", size="xs", className="kmviz-figure-select"),
                    cf.number(self.f("legend_font_size"), label="Font size", leftSection=icons("font_size"), min=0, max=100, value=None, step=1, placeholder="10", size="xs"),
                    cf.color(self.f("legend_font_color"), label="Font color", size="xs", value="#000000")
                )
            ],
            value="entry"
        )

    def layout(self):
        return cf.tabs(
            self.f["legend"],
            cf.tabs_list(
                self.f["legend-tabslist"],
                cf.tabs_tab(self.f["title-tab"], "Title", value="title"),
                cf.tabs_tab(self.f["position-tab"], "Position", value="position"),
                cf.tabs_tab(self.f["entry-tab"], "Entry", value="entry"),
                cf.tabs_tab(self.f["box-tab"], "Box", value="box"),
                dmc.Space(w=10),
                cf.switch(self.f("showlegend"), checked=True, size="lg", offLabel="Show", onLabel="Hide", style = {"margin-top": "2px"}, color=km_color),
            ),
            self._title_panel(),
            self._position_panel(),
            self._entry_panel(),
            self._box_panel(),
            value=None
        )

    def callbacks(self):

        @callback(
            Output(self.fid, "figure", allow_duplicate=True),
            inputs=dict(inputs=(
                Input(self.fid, "figure"),
                Input(kid.kmviz("auto"), "checked"),
                Input(self.f("showlegend"), "checked"),
                Input(self.f("legend_title_text"), "value"),
                Input(self.f("legend_title_font_size"), "value"),
                Input(self.f("legend_title_font_family"), "value"),
                Input(self.f("legend_title_font_color"), "value"),
                Input(self.f("legend_title_side"), "value"),
                Input(self.f("legend_font_size"), "value"),
                Input(self.f("legend_font_family"), "value"),
                Input(self.f("legend_font_color"), "value"),
                Input(self.f("legend_borderwidth"), "value"),
                Input(self.f("legend_bordercolor"), "value"),
                Input(self.f("legend_bgcolor"), "value"),
                Input(self.f("legend_indentation"), "value"),
                Input(self.f("legend_orientation"), "value"),
                Input(self.f("legend_xanchor"), "value"),
                Input(self.f("legend_xref"), "value"),
                Input(self.f("legend_x"), "value"),
                Input(self.f("legend_yanchor"), "value"),
                Input(self.f("legend_yref"), "value"),
                Input(self.f("legend_y"), "value"),
            )),
            prevent_initial_call=True,
            prevent_initial_callbacks= True
        )
        def update_legend(inputs):
            if ctx.triggered_id == self.fid:
                if not inputs[1]:
                    return no_update
                return patch_figure_all(ctx, ["layout"], set([self.fid, kid.kmviz("auto", True)]))
            return patch_figure(ctx)