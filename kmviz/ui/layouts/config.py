from dash_extensions.enrich import html, Input, Output, State, callback, clientside_callback
from kmviz.core.config import state

from dash import Patch

from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import khide, kshow
from kmviz.ui.utils import make_select_data

from kmviz.ui.components.option import make_user_option, RangeOption

from dash_iconify import DashIconify

class ConfigLayout:
    def __init__(self, st: state):
        self.st = st
        self.opt = kid.config.new("opt")

    def _db_layout(self):
        layout = []

        for db_name in self.st.engine.list():
            db = self.st.engine.get(db_name)
            children = []

            if db.has_visible_options:
                for opt in db.options.values():
                    if opt.hidden:
                        continue
                    children.append(make_user_option(opt, id=self.opt(f"{db_name}-{opt.name}")))
            layout.append(cf.div(
                kid.config(db_name),
                *children,
                style=kshow if db_name == self.st.defaults.configuration else khide
            ))
        return layout

    def _option_callback(self, name, opt_name):
        def update(value):
            patch = Patch()
            patch[name][opt_name] = value
            return patch
        return update

    def _option_slider_callback(self, opt_name):
        def update(value):
            return [f"{opt_name} = {value}"]
        return update

    def _db_callbacks(self):
        for db_name, db in self.st.engine.all().items():
            for opt_name in db.options:
                if db.options[opt_name].hidden:
                    continue
                callback(
                    Input(self.opt(f"{db_name}-{opt_name}"), "value"),
                    Output(kid.store("options"), "data"),
                    prevent_initial_call=True
                )(self._option_callback(db_name, opt_name))
                if isinstance(db.options[opt_name], RangeOption):
                    idx = self.opt(f"{db_name}-{opt_name}")
                    callback(
                        Input(idx, "value"),
                        Output(f"{idx['type']}-{idx['index']}-{opt_name}", "children"),
                    )(self._option_slider_callback(opt_name))

    def layout(self):
        databases = self.st.engine.list()

        data, value = [], None
        if self.st.defaults.configuration:
            data = make_select_data(self.st.defaults.database)
            value = self.st.defaults.configuration

        show_conf = True

        if self.st.defaults.hide:
            db_name = self.st.defaults.database[0]
            show_conf = self.st.engine.get(db_name).has_visible_options
        else:
            show_conf = any(self.st.engine.get(db_name).has_visible_options for db_name in databases)

        show_select = show_conf and not self.st.defaults.hide

        return cf.div(
            kid.config["div"],
            cf.divider(size="sm", color="gray", label="CONFIGURATION", labelPosition="center"),
            cf.select(
                kid.config["select"],
                clearable=True,
                data=data,
                value=value,
                leftSection=DashIconify(icon="mynaui:config"),
                style=kshow if show_select else khide
            ),
            *self._db_layout(),
            style = kshow if show_conf else khide
        )

    def callbacks(self) -> None:

        clientside_callback(
            """
            function(database, ids) {
                styles = Array(ids.length);
                styles.fill({"display": "none"});
                if (!database) {
                    return styles;
                }
                for (let i = 0; i < ids.length; i++) {
                    if (ids[i]["index"] === database) {
                        styles[i]["display"] = "inline";
                    } else {
                        styles[i]["display"] = "none";
                    }
                }
                return styles;
            }
            """,
            Input(kid.config["select"], "value"),
            State(kid.config.all, "id"),
            Output(kid.config.all, "style"),
            prevent_initial_call=True
        )

        self._db_callbacks()