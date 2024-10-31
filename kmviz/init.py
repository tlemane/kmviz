from kmviz.core import KmVizError
from kmviz.core.config import state
from kmviz.core.log import kmv_info

from kmviz.ui.components.factory import dmc_new
import dash

if dmc_new:
    dash._dash_renderer._set_react_version('18.2.0')

import dash_auth
from dash_extensions.enrich import DashProxy, LogTransform, NoOutputTransform, ServersideOutputTransform
from dash_extensions.enrich import html
import dash_mantine_components as dmc

from kmviz.api import KmvizAPI

import keyring


from dash_mantine_components import __version__ as dmc_version

def make_auth_function(usernames):
    def auth_function(username, password):
        if username not in usernames:
            return False
        p = keyring.get_password("kmviz", username)
        if p == password:
            return True
        return False
    return auth_function

def make_auth(application, config):
    if isinstance(config, dict):
        return dash_auth.BasicAuth(application, config)
    elif isinstance(config, list):
        return dash_auth.BasicAuth(application, auth_func=make_auth_function(set(config)))
    else:
        raise KmVizError("auth configuration is not valid")

def make_kmviz_app(st: state):
    app = DashProxy(
        __name__,
        transforms=[
            LogTransform(),
            NoOutputTransform(),
            ServersideOutputTransform(backends=[st.caches.server]),
        ],
        prevent_initial_callbacks=True,
        suppress_callback_exceptions=True,
        use_pages=True,
        pages_folder="ui/pages",
        background_callback_manager=st.caches.manager,
        external_stylesheets=st.css,
        external_scripts=st.js,
        meta_tags=st.html.metatags
    )

    if st.html.template:
        app.index_string = st.html.template

    if dmc_new:
        app.layout = dmc.MantineProvider([
            dash.page_container
        ])
    else:
        app.layout = html.Div([
            dash.page_container
        ])

    for page in dash.page_registry.values():
        kmv_info(f"📄 {page['name']} (path: '{page['path']}', relative_path: '{page['relative_path']}')")

    if st.auth:
        make_auth(app, st.auth)

    KmvizAPI(st, app.server)
    st.init_plugins_api(app.server)

    return app
