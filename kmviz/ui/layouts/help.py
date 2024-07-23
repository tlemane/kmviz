from kmviz.core.config import state
from kmviz.ui.components.factory import ComponentFactory as cf
from dash_extensions.enrich import html, dcc
import kmviz

class HelpLayout:
    def __init__(self, st: state, factory):
        self.st = st
        self.f = factory

    def layout(self):
        ph = []
        p_header = cf.div(self.f["plugin-header"])

        if self.st.conf.plugins:
            for name, plugin in self.st.conf.plugins.items():
                if h := plugin.help():
                    ph.append(h)
            if ph:
                p_header = cf.div(
                    self.f["plugin-header"],
                    html.H2("Plugins"),
                    html.P("The <b>kmviz</b> instance has loaded one or more plugins. You may find some help below, when provided.")
                )

        return cf.div(
            self.f["div"],
            html.H1(f"kmviz {kmviz.__version_str__}"),
            html.H2("Links"),
            html.Ul(
                [html.Li(dcc.Link("Github", href="https://github.com/tlemane/kmviz", target="_blank")),
                html.Li(dcc.Link("Documentation", href="https://tlemane.github.io/kmviz", target="_blank"))]
            ),
            *ph
        )

    def callbacks(self):
        pass
