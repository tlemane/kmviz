from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.utils import icons
from dash_extensions.enrich import Input, State, Output, callback, ctx
from kmviz.ui.layouts.figure import patch_figure

class SliderLayout:
    def __init__(self, factory, figure_id, axis):
        self.f = factory
        self.fid = figure_id
        self.axis = axis

    def layout(self):
        return cf.group(
            self.f["slider-grp-1"],
            cf.switch(self.f("rangeslider_visible"), onLabel="ON", offLabel="OFF", checked=False, size="lg", className="kmviz-figure-switch"),
            cf.number(self.f("rangeslider_borderwidth"), min=0, value=1, max=100, step=1, leftSection=icons("cline"), label="Width", size="xs"),
            cf.number(self.f("rangeslider_thickness"), min=0.0, value=0.1, max=1, step=0.01, decimalScale=2, leftSection=icons("floating"), label="Thickness", size="xs"),
            cf.segmented(self.f("rangeslider_yaxis_rangemode"), ["auto", "fixed", "match"], value="auto", className="kmviz-figure-segmented", size="xs"),
            cf.color(self.f("rangeslider_bordercolor"), size="xs", label="Border color", value=None),
            cf.color(self.f("rangeslider_bgcolor"), size="xs", label="Bg color", value=None),
        )

    def callbacks(self):
        @callback(
            Output(self.fid, "figure"),
            inputs=dict(inputs=(
                State(self.axis, "value"),
                Input(self.f("rangeslider_visible"), "checked"),
                Input(self.f("rangeslider_borderwidth"), "value"),
                Input(self.f("rangeslider_thickness"), "value"),
                Input(self.f("rangeslider_bordercolor"), "value"),
                Input(self.f("rangeslider_bgcolor"), "value"),
                Input(self.f("rangeslider_yaxis_rangemode"), "value"),
            )),
            prevent_initial_call=True,
        )
        def update_rs(inputs):
            n = "xaxis" if inputs[0] == 0 else f"xaxis{inputs[0]+1}"
            return patch_figure(ctx, ["layout", n])
