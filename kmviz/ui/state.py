from kmviz.core.provider import Providers, make_provider_from_dict
from kmviz.core.cache import result_cache_manager, callback_manager
from kmviz.core import KmVizError
from kmviz.core.plugin import installed_plugins, search_for_plugins
from kmviz.core.log import kmv_info
from importlib_resources import files
import shutil

class kState:
    def __init__(self):
        self._providers: Providers = Providers()
        #self.queries = []
        #self.results = {}
        self.dashboard_path = None
        self._manager = None
        self._cache = None
        self._plugins = {}
        self._external_css = []
        self._external_js = []

    def store_result(self, uid: str, results: tuple):
        self._cache[uid] = results
        self._cache.close()

    def get_result(self, uid: str) -> tuple:
        res = self._cache[uid]
        self._cache.close()
        return res

    def configure(self, config: dict):
        self._configure_plugins(config)
        self._configure_providers(config)
        self._configure_caches(config)

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
    def css(self):
        return self._external_css

    @property
    def js(self):
        return self._external_js

    def instance_plugin(self):
        for name, p in self._plugins.items():
            if p.is_instance_plugin():
                return p
        return None

    def _configure_caches(self, config: dict):
        if "manager" not in config:
            raise KmVizError("'manager' section is missing in the configuration file.")
        self._manager = callback_manager(config["manager"])

        if "cache" not in config:
            raise KmVizError("'cache' section is missing in the configuration file.")
        self._init_cache(config["cache"])

    def _init_cache(self, params: dict):
        self._cache = result_cache_manager(params["params"])

    def _configure_plugins(self, config: dict):
        installed = installed_plugins()
        kmv_info(f"Installed plugins: {','.join(installed)}")

        if not "plugins" in config:
            self.dashboard_path = "/"
        else:
            self._plugins = search_for_plugins(config["plugins"])
            for name, plugin in self._plugins.items():
                self._external_css.extend(plugin.external_styles())
                self._external_js.extend(plugin.external_scripts())
                self._copy_plugin_assets(name)

    def _copy_plugin_assets(self, plugin_name):
        p = files(plugin_name).joinpath("assets")
        main = str(files("kmviz").joinpath("assets"))
        if p.exists() and p.is_dir():
            shutil.copytree(p, f"{main}/_{plugin_name}_assets", dirs_exist_ok=True)

    def _configure_providers(self, config: dict):
        if "providers" not in config:
            raise KmVizError("'providers' section is missing in the configuration file.")

        for config in config["providers"]:
            for provider, params in config.items():
                kmv_info(f"Load provider '{provider}'")
                p = make_provider_from_dict(provider, params)
                try:
                    kmv_info(f"Init provider '{provider}'")
                    p.connect()
                except:
                    raise KmVizError("Init fails for '{provider}'")
                self._providers.add(p)

def init_state():
    global kmstate
    kmstate = kState()

