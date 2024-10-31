from dash_extensions.enrich import callback, Input, State, Output
from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.core.config import state
from dash import html

class Global:
    def __init__(self, st: state):
        self.st = st

    def _store(self):

        default_options = {}
        for db_name in self.st.engine.list():
            default_options[db_name] = {}
            for opt_name, opt in self.st.engine.get(db_name).options.items():
                default_options[db_name][opt_name] = opt.value if opt.value else opt.default

        default_options["notif"] = {}
        for name, opt in self.st.notif.options().items():
            default_options["notif"][name] = opt.value if opt.value else opt.default

        return cf.div(
            kid.store["div"],
            cf.store(kid.pom["store"], data={}),
            cf.store(kid.store["session-id"], data=None),
            cf.store(kid.store("sequences"), data=[]),
            cf.store(kid.store("options"), data=default_options),
            cf.store(kid.store("databases"), data=self.st.defaults.database),
            cf.store(kid.store["state"], data={}),
            cf.store(kid.store["results"], data={}),
            cf.store(kid.store["presets"], data={}),
            html.Div(id=kid.submit["notification"]),
        )

    def _store_callbacks(self) -> None:
        @callback(
            Input(kid.store.all, "data"),
            State(kid.store.all, "id"),
            State(kid.store["state"], "data"),
            Output(kid.store["state"], "data"),
            Output(kid.submit["button"], "disabled"),
            prevent_initial_call=True
        )
        def is_ready(stores, ids, data):
            if "submit" in data and data["submit"]:
                return data, True

            r = {
                ids[index]["index"]: store is not None and len(store)
                for index, store in enumerate(stores)
            }

            if all(r.values()):
                r["submit"] = True
            else:
                r["submit"] = False

            return r, not r["submit"]

    def layout(self):
        return cf.div(
            kid.kmviz["global-div"],
            self._store()
        )

    def callbacks(self):
        self._store_callbacks()
