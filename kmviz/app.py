import click
import dash
from dash_extensions.enrich import DashProxy, LogTransform, NoOutputTransform, ServersideOutputTransform, html
import dash_bootstrap_components as dbc
from kmviz.core.log import kmv_info, instance_id, setup_logger, kmv_ex
from kmviz.core.provider import make_provider_from_dict
from kmviz.core.cache import callback_manager
from kmviz.core import KmVizError

import dash_auth

import os
from kmviz.ui import state
state.init_state()
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import tomli

def make_app():
    app = DashProxy(
        __name__,
        transforms=[
            LogTransform(),
            NoOutputTransform(),
            ServersideOutputTransform(),
        ],
        prevent_initial_callbacks=True,
        use_pages=True,
        pages_folder="ui/pages",
        background_callback_manager=state.kmstate.manager,
        external_stylesheets=state.kmstate.css,
        external_scripts=state.kmstate.js,
    )

    app.layout = html.Div([
        dash.page_container
    ])

    return app

def init(**kwargs):
    if not kwargs:
        kwargs["config"] = os.environ["KMVIZ_CONF"]

    setup_logger()
    kmv_info(f"Starting kmviz (instance_id = {instance_id()})")

    cpath = kwargs["config"]
    config = None
    with open(cpath, "rb") as config_file:
        if cpath.endswith(".toml"):
            config = tomli.load(config_file)
        elif cpath.split(".")[-1] in ("yml", "yaml"):
            config = load(config_file, Loader=Loader)
        else:
            raise KmVizError("Invalid config file format, supported formats are 'yaml' and 'toml'.")

    state.kmstate.configure(config)

    return config

@click.command()
@click.option("--config",
              help="Path to yaml config file.")
@click.option("--log-level",
              help="Logging level.",
              default="debug",
              type=click.Choice(["debug", "info", "warning", "error"]))
@click.option("--host",
              help="host",
              default="127.0.0.1")
@click.option("--port",
              help="port",
              default=8050)
@click.option("--debug",
              help="Run flask server in debug mode",
              is_flag=True)
def main(**kwargs):
    setup_logger()
    kmv_info(f"Starting kmviz (instance_id = {instance_id()})")

    config = None
    try:
        config = init(**kwargs)
    except Exception as e:
        kmv_ex(e)
        exit(1)

    app = make_app()

    if "auth" in config:
        auth = dash_auth.BasicAuth(app, config["auth"])

    app.run_server(debug=kwargs["debug"], host=kwargs["host"], port=kwargs["port"])

if __name__ == "__main__":
    main()

config = init()
app = make_app()

if "auth" in config:
    auth = dash_auth.BasicAuth(app, config["auth"])
app = app.server





