import click
import sys
import os

from kmviz.core.log import kmv_info, kmv_error, kmv_warn, kmv_ex, kmv_debug
from kmviz.core.log import setup_logger
from kmviz.api import KmvizAPI

from kmviz.core import KmVizError
from typing import Any
import json

from kmviz.core.io import make_url
import kmviz.core.config as kconf
from kmviz.init import make_kmviz_app

from contextlib import redirect_stdout

from multiprocessing import cpu_count
from flask import Flask

from kmviz import __version__ as kmviz_version

import requests

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def check_input_path(config, skip):
    if not skip and config is None:
        kmv_error("Path to config file is empty. Use 'kmviz app -c/--config <path>' or set KMVIZ_CONF env variable")
        exit(1)

def epilog(page: str=None) -> str:
    EPILOG = """
    \b
    ---
    kmviz v{v}
    Check out our documentation at {url}
    Contact: teo.lemane@genoscope.cns.fr
    ---
    """
    base="https://tlemane.github.io/tlemane/kmviz"
    return EPILOG.format(url=base if not page else f"{base}/page", v=kmviz_version)

@click.group(epilog=epilog())
@click.option("--verbose", "-v", type=click.Choice(["debug", "info", "warn", "error"]), help="Verbosity level", default="info", show_default=True)
@click.option("--log-dir", "-d", type=str, metavar="<dir>", default="", help="Path to log directory")
@click.option("--demo", "-x", type=str, default=None, hidden=True, help="Demo mode")
def kmviz(verbose, log_dir, demo):
    setup_logger(verbose, log_directory=log_dir, traceback=0 if verbose != "debug" else None)

    if demo is not None:
        import kmviz
        kmviz._set_version_str(demo)

@kmviz.command()
def version():
    """
    Show version and exit
    """
    import kmviz
    print(f"kmviz v{kmviz.__version__}")

@click.group(help="Query kmviz REST API", epilog=epilog())
@click.option("--url", "-u", default="http://localhost", help="Host", show_default=True, metavar="<str>")
@click.option("--port", "-p", default=None, help="Port", show_default=True, type=int, metavar="<int>")
@click.option("--auth", "-a", default=None, help="HTTP BasicAuth credentials", metavar="<user>:<password>")
@click.pass_context
def api(ctx, **kwargs):
    ctx.ensure_object(AttrDict)
    ctx.obj = AttrDict(**kwargs)

    if ctx.obj.auth:
        try:
            ctx.obj.auth = tuple(ctx.obj.auth.split(":", 1))
        except:
            kmv_error("Invalid auth format")
            exit(1)

    auth_text = ctx.obj.auth[0] if ctx.obj.auth else None
    kmv_info("url={url}, port={port}, auth={auth_text}", auth_text=auth_text, **kwargs)

@api.command(epilog=epilog())
@click.option("--route", "-r", default="/api", help="Route", show_default=True, metavar="<str>")
@click.option("--output", "-o", default="stdout", help="Output file", show_default=True, metavar="<path>")
@click.pass_context
def infos(ctx, route, output):
    """
    Get databases information
    """
    url = make_url(url=ctx.obj.url, port=ctx.obj.port, route=route)

    try:
        res = requests.get(url=url, allow_redirects=True, auth=ctx.obj.auth, headers={'content-type': 'application/json'})
    except Exception as e:
        kmv_error(e)
        exit(1)

    if res.status_code != 200:
        kmv_error(f"GET [{res.status_code}]: {res.content.decode()}")
        exit(1)

    kmv_info(f"GET {url} -> status {res.status_code}")

    if output != "stdout":
        with open(output, "w") as f:
            with redirect_stdout(f):
                print(json.dumps(res.json(), indent=4))
    else:
        print(json.dumps(res.json(), indent=4))

@api.command(epilog=epilog())
@click.option("--route", "-r", default="/api/query", help="Query route", show_default=True, metavar="<str>")
@click.option("--output", "-o", default="stdout", help="Output file", show_default=True, metavar="<path>")
@click.option("--database", "-d", required=True, multiple=True, help="Database to query", metavar="<str>")
@click.option("--opt", "-x", nargs=3, multiple=True, help="Database options", metavar="<db_name> <opt_name> <value>")
@click.option("--fastx", "-f", required=True, help="Path to fastx query file", metavar="<path>")
@click.pass_context
def query(ctx, route, output, database, opt, fastx):
    """
    Make queries and get results as a json session file, viewable using a local kmviz instance. See kmviz app start session
    """
    data = []
    for db in database:
        data.append(("database", db))

    for db, o, v in opt:
        if db not in database:
            raise KmVizError(f"Set '{o}' for '{db}', but '{db}' not in {database}")
        data.append((f"{db}#{o}", v))

    url = make_url(url=ctx.obj.url, port=ctx.obj.port, route=route)
    try:
        res = requests.post(url=url, data=data, files={"fastx": open(fastx, "rb")}, allow_redirects=True, auth=ctx.obj.auth)
    except Exception as e:
        kmv_error(e)
        exit(1)

    if res.status_code != 200:
        kmv_error(f"GET [{res.status_code}]: {res.content.decode()}")
        exit(1)

    kmv_info(f"POST {url} -> status {res.status_code}")

    if output != "stdout":
        with open(output, "w") as f:
            with redirect_stdout(f):
                print(json.dumps(res.json(), indent=4))
        kmv_info(output)
    else:
        print(json.dumps(res.json(), indent=4))


@api.command(epilog=epilog())
@click.option("--route", "-r", default="/api/query", help="Query route", show_default=True, metavar="<str>")
@click.option("--output", "-o", default=os.getcwd(), help="Output directory", show_default=True, metavar="<dir>")
@click.option("--database", "-d", required=True, help="Database to query", metavar="<str>")
@click.option("--opt", "-x", nargs=2, multiple=True, help="Database option, -x <opt_name> <value>", metavar="<opt_name> <value>")
@click.option("--fastx", "-f", required=True, help="Path to fastx query file", metavar="<path>")
@click.pass_context
def metadata(ctx, route, output, database, opt, fastx):
    """
    Make queries and get results as a tsv dataframe
    """
    data = []

    db_route = f"{route}/{database}"

    for o, v in opt:
        data.append((o, v))

    url = make_url(url=ctx.obj.url, port=ctx.obj.port, route=db_route)

    try:
        res = requests.post(url=url, data=data, files={"fastx": open(fastx, "rb")}, allow_redirects=True, auth=ctx.obj.auth)
    except Exception as e:
        kmv_error(e)
        exit(1)

    if res.status_code != 200:
        kmv_error(f"POST [{res.status_code}]: {res.content.decode()}")
        exit(1)

    kmv_info(f"POST {url} -> status {res.status_code}")

    filename = res.headers["Content-Disposition"].split("filename=")[1]

    with open(filename, "wb") as fout:
        fout.write(res.content)

    kmv_info(filename)

@click.group(epilog=epilog())
@click.option("--config", "-c",
              help="Path to config file",
              show_default=bool(os.environ.get("KMVIZ_CONF")),
              envvar="KMVIZ_CONF",
              show_envvar=True,
              metavar="<path>")
@click.pass_context
def app(ctx, **kwargs):
    """
    Start kmviz
    """
    ctx.ensure_object(AttrDict)
    ctx.obj = AttrDict(**kwargs)

@app.command(epilog=epilog())
@click.argument("mode", type=click.Choice(["db", "session", "plot", "api"]), default="db")
@click.option("--url", "-u", default="localhost", help="url", show_default=True, metavar="<str>")
@click.option("--port", "-p", default=8050, help="port", show_default=True, type=int, metavar="<int>")
@click.option("--no-seq-tab", is_flag=True)
@click.option("--debug", "-d", is_flag=True)
@click.pass_context
def start(ctx, mode, url, port, no_seq_tab, debug):
    """
    Start with flask server (recommended for single users)

    \b
    Mode:
      - db (default)
      - session: Session mode, see https://tlemane/github.io/kmviz/)
      - plot: Plot mode, see https://tlemane/github.io/kmviz/)
      - api: Only start the kmviz REST API (see https://tlemane/github.io/kmviz/)
    """
    kconf.init_global_state()
    check_input_path(ctx.obj.config, mode == "session" or mode == "plot")
    kconf.st.configure(mode if mode != "api" else "db", ctx.obj.config)

    if no_seq_tab:
        kconf.st.ui.with_sequence_tab = False

    if mode == "api":
        app = Flask(__name__)
        kconf.st._config.api.enabled = True
        KmvizAPI(kconf.st, app)
    else:
        app = make_kmviz_app(kconf.st)

    app.run(host=url, port=port, debug=debug)


import gunicorn.app.base

class GunicornApp(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or None
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

@app.command(epilog=epilog())
@click.option("--mode", "-m", default="db", type=click.Choice(["db", "api"]), show_default=True, metavar="<str>", help="Mode, 'db' or 'api'")
@click.option("--url", "-u", default="localhost", help="Host", show_default=True, metavar="<str>")
@click.option("--port", "-p", default=8000, help="Port", show_default=True, type=int, metavar="<int>")
@click.option("--workers", "-w", default=cpu_count() * 2 + 1, help="Number of workers", show_default=True, type=int, metavar="<int>")
@click.option("--reload-extra-file", "-r", multiple=True, type=str, metavar="<str>", help="Reload when files change")
@click.option("--extra", "-e", multiple=True, type=(str, str), help="Extra gunicorn options",metavar="<option> <value>")
@click.pass_context
def deploy(ctx, mode, url, port, workers, reload_extra_file, extra):
    """
    Deployment with gunicorn (recommended for multi-user instances)
    """
    options = {
        "bind": f"{url}:{port}",
        "workers": workers,
        "reload_extra_files": reload_extra_file,
        "reload": True if reload_extra_file else False
    }

    for opt in extra:
        if opt[0] not in options:
            options[opt[0]] = opt[1]

    kconf.init_global_state()
    kconf.st.configure("db", ctx.obj.config)

    if mode == "api":
        app = Flask(__name__)
        kconf.st._config.api.enabled = True
        KmvizAPI(kconf.st, app)
    else:
        app = make_kmviz_app(kconf.st)
    GunicornApp(app.server, options).run()


@click.group(epilog=epilog())
def config():
    """
    Configuration helpers
    """
    pass

@config.command(epilog=epilog())
@click.option("--config", "-c", required=os.environ.get("KMVIZ_CONF", None) is None,
              help="Path to config file",
              default=lambda: os.environ.get("KMVIZ_CONF"),
              show_default=os.environ.get("KMVIZ_CONF"),
              metavar="<path>")
@click.option("--with-init", "-w", is_flag=True, help="Try to init")
@click.option("--details", "-d", is_flag=True, help="Show schema on error")
def check(config, with_init, details):
    """
    Valid configuration file.
    \b
    With --with-init, the validation process also tries to init the app,
    i.e. connect to databases, load plugins, etc
    """
    from kmviz.core.config import ckmviz, parse_config
    from jsonschema import validate
    schema = ckmviz.model_json_schema(schema_generator=CustomJsonSchema)
    instance = parse_config(config)

    try:
        validate(instance=instance, schema=schema)
    except Exception as e:
        if details:
            kmv_error(e)
        else:
            kmv_error(e.message)
        exit(1)

    kmv_info("✅ Schema ok!")

    if with_init:
        try:
            setup_logger("ERROR")
            kconf.init_global_state()
            kconf.st.configure("db", config, True)
            setup_logger("DEBUG")
            kmv_info("✅ Init ok!")
        except Exception as e:
            kmv_error(f"❌ Init fails: '{str(e)}'")
            exit(1)


from pydantic_core import PydanticOmit, core_schema
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

class CustomJsonSchema(GenerateJsonSchema):
    def handle_invalid_for_json_schema(
        self, schema: core_schema.CoreSchema, error_info: str
    ) -> JsonSchemaValue:
        raise PydanticOmit

@config.command(epilog=epilog())
@click.option("--output", "-o", default="stdout", help="Output file prefix", show_default=True, metavar="<path>")
def schema(fmt, output):
    """
    Make JSON schema
    """
    from kmviz.core.config import ckmviz
    schema = json.dumps(ckmviz.model_json_schema(schema_generator=CustomJsonSchema), indent=4)

    if output != "stdout":
        with open(f"{output}.json", "r") as f:
            with redirect_stdout(f):
                print(schema)
    else:
        print(schema)

def convert_to(data: dict, format: str):
    import tomli_w
    from yaml import Dumper, dump

    if format == "json":
        return json.dumps(data, indent=4)
    elif format == "toml":
        return tomli_w.dumps(data)
    elif format == "yaml":
        return dump(data, Dumper=Dumper)

from kmviz.core.config import *

@config.command(epilog=epilog())
@click.option("--fmt", "-f", type=click.Choice(["toml", "yaml", "json"]), default="yaml", help="File format", show_default=True)
@click.option("--section", "-s", type=click.Choice(["all", "databases", "input", "api", "auth", "default", "plugins", "cache", "html"]), multiple=True, default=["all"], show_default=True)
@click.option("--output", "-o", default="stdout", help="Output file prefix", show_default=True, metavar="<path>")
def template(fmt, section, output):
    """
    Make configuration templates
    """
    if "all" in section:
        section=None

    cache = ccache.model_construct(
        result=cchachelib(type="disk", params=ccachelib_disk(cache_dir=".kmviz/result")),
        server=cchachelib(type="disk", params=ccachelib_disk(cache_dir=".kmviz/server")),
        manager=ccachemanager(type="disk", params=ccachemanager_disk(directory=".kmviz/manager")),
    )

    html = chtml.model_construct(
        template="template.html",
        metatags=dict(description="kmviz ex description")
    )

    databases = {
        "ExampleDB": cdatabase.model_construct(
            type="kmindex-server",
            params={"url": "127.0.0.1", "port": 8080},
            metadata=cmetadb.model_construct(
                type="tsv",
                params={
                    "path": "./metadata.tsv",
                    "sep": "\t",
                    "idx": "Sample",
                    "geodata": {"latitude": "Lat", "longitude":"Long"}
                }
            ),
            defaults={
                "z" : {"value": 2, "hide": True},
                "coverage" : {"value": 0.1, "hide": False}
            },
            presets="./presets.toml"
        )
    }

    default = cdefault(database="ExDB", configuration="ExampleDB")
    plugins = { "kmviz_example": {}}

    auth = {"ex_user": "ex_password"}

    c = ckmviz.model_construct(
        databases=databases,
        default=default,
        cache=cache,
        html=html,
        plugins=plugins,
        auth=auth
    ).model_dump(include=section, exclude="idx")

    if output != "stdout":
        with open(f"{output}.{fmt}", "w") as f:
            with redirect_stdout(f):
                print(schema)
    else:
        print(convert_to(c, fmt))


@click.group(epilog=epilog())
def plugin():
    """
    Plugin helpers
    """
    pass

@plugin.command(epilog=epilog())
def list():
    """
    List installed plugins
    """
    from kmviz.core.plugin import installed_plugins
    print(installed_plugins())

groups = [
    "kmviz",
    "store",
    "side",
    "input",
    "index",
    "table",
    "map",
    "plot",
    "sequence",
    "config"
]

@plugin.command("list-id", hidden=True)
@click.option("--group", "-g", type=click.Choice(groups), required=True, help="Identifier group")
@click.option("--fmt", "-f", is_flag=True, help="Formatted output")
@click.option("--string", "-s", is_flag=True, help="With string ids")
@click.option("--index", "-i", is_flag=True, help="With dict ids")
def idx(group, fmt, string, index):
    """
    List kmviz component identifiers

    \b
    This command is hidden in kmviz help and mainly
    used as a helper for writing documentation
    """
    from kmviz.ui.id_factory import kid, _split_idx, _formatted_idx
    from kmviz.ui.layouts import Global
    from kmviz.ui.layouts.sidebar import Sidebar
    from kmviz.ui.layouts.tabs import Tabs

    kconf.init_global_state()
    kconf.st.configure(None, None)
    kconf.st._mode = "db"

    Global(kconf.st).layout()
    Sidebar(kconf.st).layout()
    Tabs(kconf.st).layout()

    grp = getattr(kid, group)

    for id in grp.get_all(False, string, index):
        if fmt:
            print(f"kid.{group}{_formatted_idx(id)} {str(id)}")
        else:
            print(id)

kmviz.add_command(api)
kmviz.add_command(app)
kmviz.add_command(config)
kmviz.add_command(plugin)

if __name__ == "__main__":
    try:
        kmviz()
    except Exception as e:
        kmv_ex(e)
