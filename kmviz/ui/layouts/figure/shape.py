from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.id_factory import IDFactory
from kmviz.ui.utils import icons
from dash_extensions.enrich import html, callback, Input, Output, no_update
from dash import Patch
from kmviz.ui.components.helpers import from_json_list, magic_json

class ShapeLayout:
    def __init__(self, factory: IDFactory, figure_id):
        self.f = factory
        self.fid = figure_id

    def layout(self) -> html.Div:
        return cf.div(
            self.f["shape-div"],
            cf.json(
                self.f("shapes"),
                placeholder='[ { "type": "circle", "x0": 0, "x1": 2, "y0": 0.1, "y1": 0.8 } ]',
                label="Shape parameters",
                value=None,
                autosize=True,
                debounce=2,
                validationError="Invalid json",
                leftSection=icons("json")
            )
        )

    def callbacks(self) -> None:

        @callback(
            Input(self.f("shapes"), "value"),
            Output(self.fid, "figure"),
            prevent_initial_call=True
        )
        def update_shapes(shapes):
            p = Patch()
            if not shapes:
                p["layout"]["shapes"] = []
            js = from_json_list(shapes, "shapes")

            if not js:
                return no_update

            all_shapes = [magic_json(x) for x in js]
            p["layout"]["shapes"] = all_shapes
            return p

