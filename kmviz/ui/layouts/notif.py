from dash_extensions.enrich import html, Input, Output, State, callback, clientside_callback
from kmviz.core.config import state

from dash import Patch

from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import khide, kshow

from kmviz.ui.components.option import make_user_option, RangeOption

from dash_iconify import DashIconify
import dash_mantine_components as dmc

class NotifLayout:
    def __init__(self, st: state):
        self.st = st
        self.opt = kid.config.new("notif")

    def _layout(self):
        layout = []
        for name, opt in self.st.notif.options().items():
            layout.append(cf.div(
                self.opt(name),
                make_user_option(opt, id=self.opt(f"notif-{opt.name}"))
            ))
        return layout

    def _option_callback(self, opt_name):
        def update(value):
            patch = Patch()
            patch["notif"][opt_name] = value
            return patch
        return update

    def _callbacks(self):
        for opt_name in self.st.notif.options().keys():
            callback(
                Input(self.opt(f"notif-{opt_name}"), "value"),
                Output(kid.store("options"), "data"),
                prevent_initial_call=True
            )(self._option_callback(opt_name))


    def layout(self):
        if not len(self.st.notif.options()):
            return cf.div(kid.config["notif-div"], style = {"display": "none"})

        return cf.div(
            kid.config["div"],
            cf.divider(size="sm", color="gray", label="NOTIFICATION", labelPosition="center"),
            *self._layout(),
            dmc.Space(h=10),
        )

    def callbacks(self) -> None:
        self._callbacks()