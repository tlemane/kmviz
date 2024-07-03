from dash_extensions.enrich import FileSystemBackend
from kmviz.core.provider import Providers, make_provider_from_dict
from kmviz.core import KmVizError
from kmviz.core.plugin import installed_plugins, search_for_plugins
from kmviz.core.log import kmv_info
from kmviz.core.provider import PROVIDERS
from kmviz.core.metadata import METADBS
from importlib_resources import files

from kmviz.core.cache import make_server_cache_manager, make_callback_cache_manager, make_result_cache_manager

import shutil

class kState:
    def __init__(self):
        self._providers: Providers = Providers()
        self.dashboard_path = "/"
        self._manager = None
        self._cache = None
        self._plugins = {}
        self._external_css = []
        self._external_js = []
        self.plot_only = False
        self._backend = None
        self._template = ""
        self._metatags = []

    def store_result(self, uid: str, results: tuple):
        self._cache.set(uid, results)

    def get_result(self, uid: str) -> tuple:
        res = self._cache.get(uid)
        if res is None:
            raise KmVizError("Not in cache.")
        return res

    def configure(self, config: dict):
        self._config = config
        self._configure_template(config)
        self._configure_plugins(config)
        self._configure_providers(config)
        self._configure_caches(config)

    @property
    def config(self):
        return self._config

    @property
    def plugins(self):
        return self._plugins

    @property
    def providers(self):
        return self._providers

    @property
    def manager(self):
        return self._manager

    @property
    def backend(self):
        return self._backend

    @property
    def css(self):
        return self._external_css

    @property
    def js(self):
        return self._external_js

    @property
    def template(self):
        return self._template

    @property
    def metatags(self):
        return self._metatags

    def instance_plugin(self):
        for name, p in self._plugins.items():
            if p.is_instance_plugin():
                if "dashboard" in p.config and p.config["dashboard"] != "/":
                    self.dashboard_path = p.config["dashboard"]
                else:
                    self.dashboard_path = "/dashboard"
                return p
        return None

    def _configure_template(self, config: dict):
        if "html" not in config:
            return

        if "template" in config["html"]:
            with open(config["html"]["template"], "r") as fin:
                self._template = fin.read()

        if "metatags" in config ["html"]:
            self._metatags = config["html"]["metatags"]
            if isinstance(self._metatags, dict):
                self._metatags = [self._metatags]

    def _configure_caches(self, config: dict):
        if "cache" not in config:
            config["cache"] = {}

        if "manager" not in config["cache"]:
            manager_default = { "type": "disk", "params": {"directory": "./kmviz_manager_cache"} }
            self._manager = make_callback_cache_manager(manager_default)
        else:
            self._manager = make_callback_cache_manager(config["cache"]["manager"])

        if "result" not in config["cache"]:
            result_params = {
                "cache_dir": "./kmviz_result_cache",
                "default_timeout": 60 * 60 * 24 * 14,
                "threshold": 0
            }
            result_default = { "type": "disk", "params": result_params }
            self._cache = make_result_cache_manager(result_default)
        else:
            self._cache = make_result_cache_manager(config["cache"]["result"])

        if "serverside" not in config["cache"]:
            server_params = {
                "cache_dir": "./kmviz_serverside_cache",
                "default_timeout": 60 * 60 * 24,
                "threshold": 0
            }
            server_default = { "type": "disk", "params": server_params }
            self._backend = make_server_cache_manager(server_default)
        else:
            self._backend = make_server_cache_manager(config["cache"]["serverside"])

    def _configure_plugins(self, config: dict):
        installed = installed_plugins()
        kmv_info(f"Installed plugins: {','.join(installed)}")

        if not "plugins" in config:
            self.dashboard_path = "/"
        else:
            self._plugins = search_for_plugins(config["plugins"])

            for name, plugin in self._plugins.items():
                if name in config["plugins"]:
                    plugin.configure(config["plugins"][name])

                self._external_css.extend(plugin.external_styles())
                self._external_js.extend(plugin.external_scripts())
                self._copy_plugin_assets(name)

                p_providers = plugin.providers()
                p_metadb = plugin.databases()

                if p_providers:
                    for pname, prov in p_providers:
                        if pname not in PROVIDERS:
                            kmv_info(f"Load external Provider '{pname}' from '{name}' plugin")
                            PROVIDERS[pname] = prov

                if p_metadb:
                    for pname, metadb in p_metadb:
                        if pname not in METADBS:
                            kmv_info(f"Load external MetaDB '{pname}' from '{name}' plugin")
                            METADBS[pname] = metadb

    def _copy_plugin_assets(self, plugin_name):
        p = files(plugin_name).joinpath("assets")
        main = str(files("kmviz").joinpath("assets"))
        if p.exists() and p.is_dir():
            shutil.copytree(p, f"{main}/_{plugin_name}_assets", dirs_exist_ok=True)

    def _configure_providers(self, config: dict):
        if "databases" not in config:
            raise KmVizError("'databases' section is missing in the configuration file.")

        for name, params in config["databases"].items():
            kmv_info(f"Load provider '{name}'")
            p = make_provider_from_dict(name, params)
            try:
                kmv_info(f"Init provider '{name}'")
                p.connect()
            except:
                raise KmVizError(f"Init fails for '{name}'")
            self._providers.add(p)

def init_state():
    global kmstate
    kmstate = kState()

