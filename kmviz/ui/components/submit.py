from dash_extensions.enrich import DashLogger, Input, Output, State, html, dcc
from dash_extensions.enrich import Serverside, callback

from dash import no_update, Patch
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import time
from kmviz.ui import state
from kmviz.ui.patch import style_hide_patch, style_inline_patch
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.utils import prevent_update_on_none, make_select_data
from kmviz.ui.components.store import ksf, ksfr
from kmviz.ui.components.select import kgsf
from kmviz.core.log import kmv_info
import time

import uuid

ksub = kf.child("submit")

def make_submit():
    res = html.Div([
        dmc.Center([
            dmc.Group([
                dmc.Button(
                    "Submit",
                    id=ksub.sid("button"),
                    leftIcon=DashIconify(icon="mdi:dna", width=20),
                    disabled=True
                ),
                html.A(
                    dmc.Button(
                        "Reset",
                        id=ksub.sid("refresh-button"),
                        leftIcon=DashIconify(icon="system-uicons:refresh", width=20),
                    ),
                    href=state.kmstate.dashboard_path
                ),
            ])
        ]),
        dmc.Space(h=10),
        html.Div([
            dmc.Progress(id=ksub.sid("progress"), value=0, size="xl", striped=True, animate=True)
        ], id=ksub.sid("progress-div"), style={"display": "none"}),
        dmc.NotificationsProvider([
            html.Div(id=kf.sid("notification")),
        ], limit=1),
    ])

    return res

def make_session_notification(action, uuid_str):
    msg="Here is your session id, use it to access your results later"
    notif = dmc.Notification(
        id="submit-notif",
        title=uuid_str,
        loading=False,
        message=msg,
        action=action,
        autoClose=False,
    )
    return notif

def make_submit_callbacks():

    @callback(
        Input(ksf("ready-state"), "data"),
        State(ksub.sid("button"), "n_clicks"),
        Output(ksub.sid("button"), "disabled")
    )
    def ready_to_submit(state, n_clicks):
        if n_clicks and n_clicks > 0:
            return True
        if all(state.values()):
            return False
        return True

    @callback(
        Output(ksf("query-results"), "data"),
        Output(kgsf("provider"), "data"),
        Output(kgsf("provider"), "value"),
        Output(kgsf("query"), "data"),
        Output(kgsf("query"), "value"),
        Output(kf.sid("session-id"), "data"),
        inputs=[
            Input(ksub.sid("button"), "n_clicks"),
            State(ksfr("query-sequences"), "data"),
            State(ksfr("provider-options"), "data"),
            State(ksfr("provider-active"), "data"),
        ],
        background=True,
        running=[
            (Output(ksub.sid("button"), "disabled"), True, True),
            (Output(ksub.sid("progress"), "animate"), True, False),
            (Output(ksub.sid("progress-div"), "style"), style_inline_patch(), style_inline_patch())
        ],
        progress=[Output(ksub.sid("progress"), "value"),
                  Output(ksub.sid("progress"), "label"),
                  Output(kf.sid("notification"), "children")],
        prevent_initial_call=True,
    )
    def submit(set_progress, n_clicks, queries, options, actives):
        prevent_update_on_none(n_clicks)

        nb_queries = len(queries)
        progress_pattern = "{n} / {total}"

        uuid_str = f"kmviz-{str(uuid.uuid4())}"

        kmv_info(f"⌛ {uuid_str}")
        nshow = make_session_notification("show", uuid_str)

        set_progress((0, progress_pattern.format(n=0, total=nb_queries), nshow))

        query_results = {}

        for i, query in enumerate(queries):
            result = state.kmstate.providers.query(query, actives, options, uuid_str)

            keys = list(result.keys())
            for key in keys:
                if isinstance(result[key], str):
                    del r[k]
            query_results[query.name] = result

            set_progress(((i / nb_queries) * 100, progress_pattern.format(n=i, total=nb_queries), nshow))

        default_query = queries[0].name
        default_provider = actives[0]

        state.kmstate.store_result(
            uuid_str,
            (query_results,
            make_select_data(actives),
            default_provider,
            make_select_data([query.name for query in queries]),
            default_query)
        )

        set_progress((100, "Done", nshow))

        kmv_info(f"✅ {uuid_str}")
        return (
            Serverside(query_results),
            make_select_data(actives),
            default_provider,
            make_select_data([query.name for query in queries]),
            default_query,
            uuid_str
        )

