from kmviz.ui.id_factory import IDFactory, kid
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.layouts.figure import patch_figure, patch_figure_all
from dash_extensions.enrich import Input, State, Output, callback, ctx, no_update
from dash import html
from kmviz.ui.utils import icons

class TitleLayout:
    def __init__(self, factory: IDFactory, figure_id):
        self.f = factory
        self.fid = figure_id

    def layout(self) -> html.Div:
        return cf.div(
            self.f["div"],
            cf.group(
                self.f["grp-1"],
                cf.text(self.f("title_text"), label="Text", placeholder="<b>Title</b>", size="xs", value=None),
                cf.number(self.f("title_font_size"), label="Size", min=1, max=100, step=1, value=16, leftSection=icons("font_size"), size="xs"),
                cf.font(self.f("title_font_family"), label="Font", size="xs"),
                cf.color(self.f("title_font_color"), label="Font color", size="xs", value="#000000")
            ),
            cf.group(
                self.f["grp-2"],
                cf.select(self.f("title_xanchor"), label="Anchor X", data=["auto", "left", "center", "right"], value="auto", leftSection=icons("single"), size="xs"),
                cf.select(self.f("title_xref"), label="Reference X", data=["container", "paper"], value="container", leftSection=icons("single"), size="xs"),
                cf.number(self.f("title_x"), label="x", min=0.0, max=1.0, step=0.01, value=None, startValue=0.5, decimalScale=2, leftSection=icons("floating"), size="xs"),
                cf.select(self.f("title_yanchor"), label="Anchor Y", data=["auto", "top", "middle", "bottom"], value="auto", leftSection=icons("single"), size="xs"),
                cf.select(self.f("title_yref"), label="Reference Y", data=["container", "paper"], value="container", leftSection=icons("single"), size="xs"),
                cf.number(self.f("title_y"), label="y", min=0.0, max=1.0, step=0.01, value=None, startValue=0.9, decimalScale=2, leftSection=icons("floating"), size="xs")
            )
        )

    def callbacks(self) -> None:

        @callback(
            Output(self.fid, "figure", allow_duplicate=True),
            inputs=dict(inputs=(
                Input(self.fid, "figure"),
                Input(kid.kmviz("auto"), "checked"),
                Input(self.f("title_text"), "value"),
                Input(self.f("title_font_size"), "value"),
                Input(self.f("title_font_family"), "value"),
                Input(self.f("title_font_color"), "value"),
                Input(self.f("title_xanchor"), "value"),
                Input(self.f("title_xref"), "value"),
                Input(self.f("title_x"), "value"),
                Input(self.f("title_yanchor"), "value"),
                Input(self.f("title_yref"), "value"),
                Input(self.f("title_y"), "value"),
            )),
            prevent_initial_call=True

        )
        def update_title(inputs):
            skip = set([self.fid, kid.kmviz("auto", True)])
            if ctx.triggered_id == self.fid:
                if not inputs[1]:
                    return no_update
                return patch_figure_all(ctx, ["layout"], skip)
            return patch_figure(ctx)
