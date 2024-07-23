from dash_extensions.enrich import Input, State, Output, callback, dcc
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color
from dash_iconify import DashIconify
import plotly.io as pio

class DownloadGraphLayout:
    def __init__(self, factory, figure_id, filename = "fig"):
        self.f = factory
        self.fid = figure_id
        self.filename = filename

    def layout(self):
        return cf.group(
            self.f["dl-grp"],
            dcc.Download(id=self.f["download"]),
            cf.segmented(
                self.f["format"],
                ["png", "jpg", "svg", "pdf", "html", "json"],
                value="png",
                size="xs",
                color=km_color
            ),
            cf.action(
                self.f["button"],
                DashIconify(icon="material-symbols:download", width=20),
                variant="filled",
                color=km_color,
            ),
            gap=3
        )

    def callbacks(self) -> None:
        @callback(
            Input(self.f["button"], "n_clicks"),
            State(self.f["format"], "value"),
            State(self.fid, "figure"),
            Output(self.f["download"], "data")
        )
        def download(n_clicks, fmt, data):
            if n_clicks:
                if fmt == "html":
                    content = pio.to_html(data, validate=False)
                    return dict(content=content, filename=f"{self.filename}.html")
                elif fmt == "json":
                    content = pio.to_json(data, validate=False)
                    return dict(content=content, filename=f"{self.filename}.json")
                else:
                    content = pio.to_image(data, fmt, validate=False)
                    return dcc.send_bytes(content, f"{self.filename}.{fmt}")
