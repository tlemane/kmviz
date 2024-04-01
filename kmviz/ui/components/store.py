from dash_extensions.enrich import html, dcc, Input, Output, State, callback
from kmviz.ui.id_factory import kmviz_factory

from kmviz.ui import state

ksf = kmviz_factory.child("store")
ksfr = ksf.child("required")

def make_stores():

    default_options = {}
    for provider_name in state.kmstate.providers.list():
        default_options[provider_name] = {}
        for opt_name, opt in state.kmstate.providers.get(provider_name).options.items():
            default_options[provider_name][opt_name] = opt.value if opt.value else opt.default

    return html.Div([
        dcc.Store(id=ksfr("query-sequences"), data=[]),
        dcc.Store(id=ksfr("provider-options"), data=default_options),
        dcc.Store(id=ksfr("provider-active"), data=[]),
        dcc.Store(id=ksf("ready-state"), data={}),
        dcc.Store(id=ksf("query-results"), data={})
    ])

def make_stores_callbacks():

    @callback(
        Output(ksf("ready-state"), "data"),
        Input(ksfr.all, "data"),
        State(ksfr.all, "id"),
        prevent_intial_callbacks=True
    )
    def update_ready_state(stores, idx):
        return {
            idx[i]["index"]: store is not None and len(store)
            for i, store in enumerate(stores)
        }
