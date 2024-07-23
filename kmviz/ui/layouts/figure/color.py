from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color
from kmviz.ui.utils import icons
from kmviz.ui.id_factory import IDFactory, kid
from dash_extensions.enrich import Input, Output, no_update, callback, ctx
from kmviz.ui.layouts.figure import patch_figure, patch_figure_all
import dash_mantine_components as dmc

class ColorLegendLayout:
    def __init__(self, factory: IDFactory, figure_id):
        self.f = factory
        self.fid = figure_id

    def _title_panel(self):
        return cf.tabs_panel(
            self.f["title-panel"],
            [
                cf.group(
                    self.f["title-grp-1"],
                    cf.text(self.f("colorbar_title_text"), label="Text", placeholder="<b>Title</b>", size="xs"),
                    cf.number(self.f("colorbar_title_font_size"), label="Font size", leftSection=icons("font_size"), min=0, max=100, value=None, step=1, placeholder="14", size="xs"),
                    cf.font(self.f("colorbar_title_font_family"), label="Font", size="xs"),
                    cf.select(self.f("colorbar_title_side"), data=["top", "bottom", "right"], label="Position", value="top", size="xs", leftSection=icons("pos"), className="kmviz-figure-select"),
                    cf.color(self.f("colorbar_title_font_color"), label="Font color", size="xs", value="#000000"),
                )
            ],
            value="title"
        )

    def _box_panel(self):
        orient = [
            {"label": "vertical", "value": "v"},
            {"label": "horizontal", "value": "h"},
        ]
        return cf.tabs_panel(
            self.f["box-panel"],
            [
                cf.group(
                    self.f["box-grp-1"],
                    cf.select(self.f("colorbar_xanchor"), label="Anchor X", data=["auto", "left", "center", "right"], value="auto", leftSection=icons("single"), size="xs"),
                    cf.select(self.f("colorbar_xref"), label="Reference X", data=["container", "paper"], value="container", leftSection=icons("single"), size="xs"),
                    cf.number(self.f("colorbar_x"), label="x", min=0.0, max=1.0, step=0.01, value=0.9, startValue=0.9, placeholder="0.5", decimalScale=2, leftSection=icons("floating"), size="xs"),
                    cf.select(self.f("colorbar_yanchor"), label="Anchor Y", data=["auto", "top", "middle", "bottom"], value="auto", leftSection=icons("single"), size="xs"),
                    cf.select(self.f("colorbar_yref"), label="Reference Y", data=["container", "paper"], value="container", leftSection=icons("single"), size="xs"),
                    cf.number(self.f("colorbar_y"), label="y", min=0.0, max=1.0, step=0.01, value=None, startValue=0.9, placeholder="0.95", decimalScale=2, leftSection=icons("floating"), size="xs"),
                    cf.number(self.f("colorbar_borderwidth"), label="Width", min=0, max=100, step=1, value=0, leftSection=icons("width", rotate=1), size="xs"),
                    cf.color(self.f("colorbar_bordercolor"), label="Border color", size="xs"),
                    cf.color(self.f("colorbar_bgcolor"), label="Bg color", size="xs"),
                )
            ],
            value="box"
        )

    def layout(self):
        return cf.tabs(
            self.f["legend"],
            cf.tabs_list(
                self.f["legend-tabslist"],
                cf.tabs_tab(self.f["title-tab"], "Title", value="title"),
                cf.tabs_tab(self.f["box-tab"], "Box", value="box"),
            ),
            self._title_panel(),
            self._box_panel(),
            value="title"
        )

    def callbacks(self):

        @callback(
            Output(self.fid, "figure", allow_duplicate=True),
            inputs=dict(inputs=(
                Input(self.f("colorbar_title_text"), "value"),
                Input(self.f("colorbar_title_font_size"), "value"),
                Input(self.f("colorbar_title_font_family"), "value"),
                Input(self.f("colorbar_title_font_color"), "value"),
                Input(self.f("colorbar_title_side"), "value"),
                Input(self.f("colorbar_borderwidth"), "value"),
                Input(self.f("colorbar_bordercolor"), "value"),
                Input(self.f("colorbar_bgcolor"), "value"),
                Input(self.f("colorbar_x"), "value"),
                Input(self.f("colorbar_xref"), "value"),
                Input(self.f("colorbar_xanchor"), "value"),
                Input(self.f("colorbar_y"), "value"),
                Input(self.f("colorbar_yref"), "value"),
                Input(self.f("colorbar_yanchor"), "value"),
            )),
            prevent_initial_call=True,
        )
        def update_legend(inputs):
            return patch_figure(ctx, ["layout", "coloraxis"])
