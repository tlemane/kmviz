from kmviz.core.config import state
import kmviz.core.config as kconf
from dash_extensions.enrich import html, callback, Serverside, Input, Output, State, no_update
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color, khide, kshow
from kmviz.ui.id_factory import kid
from kmviz.ui.utils import make_select_data
from kmviz.core.log import kmv_info, kmv_warn, kmv_error
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from kmviz.core import KmVizQueryError, KmVizQueryErrorNotif
import uuid

class SubmitLayout:
    def __init__(self, st: state):
        self.st = st
        self._def_tab = "table"


    def _make_notif_msg(self, current: int, nb_queries: int) -> str:
        return f"[{current}/{nb_queries}]"

    def _update_submit_notification(self, title, message):
        return dmc.Alert(
            f"Processing... {message} {self.st.ui.ui_notif_msg}",
            title=title,
            icon=DashIconify(icon="eos-icons:hourglass", width=30),
            color=km_color,
            withCloseButton=True,
            className = "kmviz-alert",
            variant="outline"
        )

    def _update_ok_submit_notification(self, title, message):
        return dmc.Alert(
            "",
            title=title if not message else f"{title} {message}",
            icon=DashIconify(icon="ep:success-filled", width=30),
            color=km_color,
            withCloseButton=True,
            className = "kmviz-alert",
            variant="outline"
        )

    def _make_error_submit_notification(self, title, msg = None):
        message = "An error occurred while processing your request(s)"

        if msg:
            message = msg

        return dmc.Alert(
            message,
            title=title,
            color="red",
            icon=DashIconify(icon="ic:twotone-error", width=30),
            withCloseButton=True,
            className = "kmviz-alert",
            variant="outline"
        )

    def _on_error(self, uuid_str, msg=None):
        return (no_update,) * 6 + (self._make_error_submit_notification(uuid_str, msg), False) + (no_update,) * 2 + (True,) * 5 + (self._def_tab, kshow, [])

    def _submit_callback(self):

        @callback(
            Input(kid.store["state"], "data"),
            State(kid.submit["button"], "n_clicks"),
            Output(kid.submit["button"], "disabled"),
            prevent_initial_call=True
        )
        def is_ready(state, n_clicks):
            #if n_clicks and n_clicks > 0:
            #    return True
            if all(state.values()):
                return False
            return True

        @callback(
            Output(kid.store["results"], "data"),
            Output(kid.kmviz("database"), "data"),
            Output(kid.kmviz("database"), "value"),
            Output(kid.kmviz("query"), "data"),
            Output(kid.kmviz("query"), "value"),
            Output(kid.store["session-id"], "data"),
            Output(kid.submit["notification"], "children"),
            Output(kid.submit["button"], "disabled"),
            Output(kid.kmviz["side-layout"], "style"),
            Output(kid.kmviz["main-layout"], "style"),

            Output(kid.tabs["index"], "disabled"),
            Output(kid.tabs["table"], "disabled"),
            Output(kid.tabs["map"], "disabled"),
            Output(kid.tabs["plot"], "disabled"),
            Output(kid.tabs["sequence"], "disabled"),
            Output(kid.tabs["tabs"], "value"),

            Output(kid.input["input-div"], "style"),
            Output(kid.input["error"], "children"),

            inputs=[
                Input(kid.submit["button"], "n_clicks"),
                State(kid.store("sequences"), "data"),
                State(kid.store("options"), "data"),
                State(kid.input("db"), "value")
            ],
            background=True,
            running=[
                (Output(kid.submit["button"], "disabled"), False, True),
                (Output(kid.submit["button"], "loading"), True, False)
            ],
            progress=[
                Output(kid.submit["notification"], "children"),
            ],
            prevent_initial_call=True
        )
        def submit(set_progress, n_clicks, sequences, options, actives):
            uuid_str = f"kmviz-{str(uuid.uuid4())}"

            nb_queries = len(sequences)

            kmv_info(f"⌛ {uuid_str}")

            results = {}

            set_progress((self._update_submit_notification(uuid_str, self._make_notif_msg(0, nb_queries))))

            try:
                kconf.st.notif.check(options["notif"])
                for i, query in enumerate(sequences):
                    result = kconf.st.engine.query(query, actives, options, uuid_str)
                    keys = list(result.keys())
                    for key in keys:
                        if isinstance(result[key], str):
                            raise KmVizQueryError(result[key])
                    results[query.name] = result
                    set_progress((self._update_submit_notification(uuid_str, self._make_notif_msg(i+1, nb_queries))))
            except KmVizQueryError as e:
                kmv_warn(f"⚠️  {uuid_str} -> {str(e)}")
                return self._on_error(uuid_str, str(e))
            except KmVizQueryErrorNotif as e:
                kmv_warn(f"⚠️  {uuid_str} -> {str(e)}")
                kconf.st.notif.send_failure(uuid_str, options["notif"], str(e))
                return self._on_error(uuid_str, str(e))
            except Exception as e:
                kmv_warn(f"⚠️  {uuid_str} -> {str(e)}")
                return self._on_error(uuid_str)

            def_query = sequences[0].name
            def_db = actives[0]

            data_db = make_select_data(actives)
            data_query = [query.name for query in sequences]

            store = (results, data_db, def_db, data_query, def_query)

            kconf.st.put(uuid_str, store)

            kmv_info(f"✅ {uuid_str}")

            notif = self._update_ok_submit_notification(f"{uuid_str}", None),

            kconf.st.notif.send_success(uuid_str, options["notif"], results)

            return (Serverside(store[0]), *store[1:], uuid_str, notif, True) + (khide, {"padding-left": "10px"}) + (False,) * 5 + (self._def_tab, khide, no_update)

    def layout(self) -> html.Div:
        return cf.div(
            kid.submit["div"],
            dmc.Space(h=10),
            dmc.Center([
                cf.group(
                    kid.submit["grp-button"],
                    cf.button(
                        kid.submit["button"],
                        "Submit",
                        leftSection=DashIconify(icon="mdi:dna", width=20),
                        disabled=True,
                        loaderProps={"type": "dots"}
                    ),
                    html.A(
                        cf.button(
                            kid.submit["reset"],
                            "Reset",
                            leftSection=DashIconify(icon="system-uicons:refresh", width=20),
                        ),
                        href=self.st.instance_plugin[0]
                    )
                )
            ]),
        )

    def callbacks(self) -> None:
        self._submit_callback()