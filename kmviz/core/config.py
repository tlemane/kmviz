from pathlib import Path

from dataclasses import dataclass
from pydantic import BaseModel, AfterValidator, ValidationInfo, ConfigDict, Field, PrivateAttr
from pydantic import model_validator, field_validator
from pydantic import PositiveInt, NonNegativeInt

from typing import List, Dict, Union, Annotated, Any, Optional, Literal, Tuple
from typing_extensions import Self

from kmviz.core import KmVizError
from kmviz.core.cache import KmvizResultCache
from kmviz.core.plugin import installed_plugins, search_for_plugin, copy_plugin_assets, copy_custom_assets
from kmviz.core.provider import Provider, Providers, PROVIDERS
from kmviz.core.metadata import MetaDB, METADBS
from kmviz.core.notifier import Notifier, NOTIFIERS, NullNotifier
from kmviz.core.query import Query, QueryResponse
from kmviz.ui.presets import cpresets

from functools import cached_property

class KmVizConfigError(KmVizError):
    pass

from kmviz.core.log import setup_logger
setup_logger()
from kmviz.core.log import kmv_info, kmv_ex, kmv_error, kmviz_idx

def wp_list(value: Any, empty: bool=False):
    if value is None:
        return list() if empty else None
    if not isinstance(value, list):
        return [value]
    return value

def parse_config(path: Union[str, dict]) -> dict:
    if isinstance(path, dict):
        return path
    else:
        path = Path(path)

    if not path.exists():
        raise KmVizConfigError(f"'{path}' does not exist!")

    res = {}
    stream = open(path, "rb")

    if path.suffix == ".json":
        import json
        res = json.load(stream)
    elif path.suffix == ".toml":
        import tomli
        res = tomli.load(stream)
    elif path.suffix == ".yaml" or path.suffix == ".yml":
        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader
        from yaml import load as yload
        res = yload(stream, Loader=Loader)
    else:
        raise KmVizConfigError(f"'{path.name}' -> Supported format are 'json', 'toml' and 'yaml'")

    stream.close()
    return res

class chtml(BaseModel):
    template: str=""
    metatags: Annotated[
        Optional[
            Union[
                Dict[str, str],
                List[Dict[str, str]]
            ]
        ],
        AfterValidator(wp_list)
    ]=None

    @field_validator("template", mode="after")
    @classmethod
    def load_html_template(cls, value: str) -> str:
        if Path(value).exists():
            with open(value, "r") as fin:
                return fin.read()
        return ""

class cdefault(BaseModel):
    database: Annotated[
        Optional[
            Union[
                str,
                List[str]
            ]
        ],
        AfterValidator(wp_list)
    ]=None
    configuration: Optional[str]=None
    hide: Optional[bool]=False

    @model_validator(mode="after")
    def check(self) -> Self:
        if isinstance(self.database, str):
            self.database = [self.database]

        if self.database and not self.configuration:
            self.configuration = self.database[0]

        return self

class ccachelib_disk(BaseModel):
    cache_dir: str
    threshold: NonNegativeInt=0
    default_timeout: PositiveInt=86400
    model_config = ConfigDict(extra="allow")

class ccachelib_redis(BaseModel):
    host: str
    port: int=6379
    db: int=0
    default_timeout: PositiveInt=86400

    model_config = ConfigDict(extra="allow")

class cchachelib(BaseModel):
    type: Literal["disk", "redis"]
    params: Union[ccachelib_disk, ccachelib_redis]

    @model_validator(mode="after")
    def check(self) -> Self:
        if self.type == "disk" and not isinstance(self.params, ccachelib_disk):
            raise ValueError(f"{self.type}")
        if self.type == "redis" and not isinstance(self.params, ccachelib_redis):
            raise ValueError(f"{self.type}")
        return self

class ccachemanager_disk(BaseModel):
    directory: str
    model_config = ConfigDict(extra="allow")

class ccachemanager_celery(BaseModel):
    pass

class ccachemanager(BaseModel):
    type: Literal["disk", "celery"]
    params: Union[ccachemanager_disk, ccachemanager_celery]

    @model_validator(mode="after")
    def check(self) -> Self:
        if self.type == "celery":
            raise ValueError("celery manager is not implemented")
        return self

class ccache(BaseModel):
    result: Annotated[
        cchachelib,
        Field(
            default_factory=lambda: cchachelib(type="disk", params=ccachelib_disk(cache_dir=".kmviz_cache/result")),
            validate_default=True
        )
    ]

    server: Annotated[
        cchachelib,
        Field(
            default_factory=lambda: cchachelib(type="disk", params=ccachelib_disk(cache_dir=".kmviz_cache/server")),
            validate_default=True
        )
    ]

    manager: Annotated[
        ccachemanager,
        Field(
            default_factory=lambda: ccachemanager(type="disk", params=ccachemanager_disk(directory=".kmviz_cache/manager")),
            validate_default=True
        )
    ]

    @field_validator("result")
    @classmethod
    def make_result_cache(cls, value: cchachelib):
        from kmviz.core.cache import make_result_cache_manager, KmvizResultCache
        return KmvizResultCache(make_result_cache_manager(value.model_dump()))

    @field_validator("server")
    @classmethod
    def make_server_cache(cls, value: cchachelib):
        from kmviz.core.cache import make_server_cache_manager
        return make_server_cache_manager(value.model_dump())

    @field_validator("manager")
    @classmethod
    def make_manager_cache(cls, value: ccachemanager):
        from kmviz.core.cache import make_callback_cache_manager
        return make_callback_cache_manager(value.model_dump())

class cinput(BaseModel):
    max_query_size: PositiveInt=2**32
    max_size: PositiveInt=2**32
    max_query: PositiveInt=2**32
    alphabet: Literal["dna", "amino", "all"]="all"

class cmetadb(BaseModel):
    type: str
    params: Dict[str, Any]

class cnotif(BaseModel):
    type: str
    success: str
    failure: str
    subject: str
    subject_failure: str
    custom: Optional[Dict[str, Any]] = {}
    params: Optional[Dict[str, Any]] = {}

class cdatabase(BaseModel):
    type: str
    params: Dict[str, Any]
    defaults: Optional[Dict[str, Any]]=None
    metadata: cmetadb
    presets: Optional[str] = Field(None, validate_default=True)

    @field_validator("presets")
    @classmethod
    def make_presets(cls, value: Optional[str]) -> cpresets:
        if value:
            res = parse_config(value)
            return cpresets(**res)
        return cpresets(priority=False, map = {}, plot = {}, defaults=None)

class cui(BaseModel):
    with_map_tab: bool=True
    with_help_tab: bool=True
    with_plot_tab: bool=True
    with_sequence_tab: bool=True
    with_index_tab: bool=True
    crs: Optional[Dict[str, Tuple[str, Dict[str, Any]]]]={}
    ui_notif_msg: Optional[str] = ""

class capi(BaseModel):
    enabled: bool=False
    with_query: bool=True
    with_download: bool=True
    route: Annotated[
        str,
        Field(default="/api", validate_default=True)
    ]
    query_route: Annotated[
        str,
        Field(default="/query", validate_default=True)
    ]
    download_route: Annotated[
        str,
        Field(default="/download", validate_default=True)
    ]
    limits: Annotated[
        cinput,
        Field(default=cinput())
    ]

    @field_validator("route", "query_route")
    @classmethod
    def check_route_syntax(cls, value: str, info: ValidationInfo):
        if value == "/":
            raise ValueError(f"'{info.field_name}' should not be '/'")
        if not value.startswith("/"):
            raise ValueError(f"'{info.field_name}' should start with '/'")
        if value.endswith("/"):
            raise ValueError(f"'{info.field_name}' ends with '/'")
        return value

def make_provider(name: str, config: cdatabase, providers: Dict[str, Provider]) -> Provider:
    if config.type not in providers:
        raise KmVizConfigError(f"Unknown provider type: '{config.type}'")

    prov = providers[config.type](name=name, **config.params)

    if config.defaults:
        prov.set_opt_defs(config.defaults)

    if config.presets:
        prov.set_presets(config.presets)

    return prov

def make_metadb(config: cmetadb, metadbs: Dict[str, MetaDB]) -> MetaDB:
    if config.type not in metadbs:
        raise KmVizConfigError(f"Unknown metadb type: '{config.type}'")
    return metadbs[config.type](**config.params)

def make_notif(config: cnotif, notifiers: Dict[str, Notifier]) -> Notifier:
    if config.type not in notifiers:
        raise KmVizConfigError(f"Unknown notifier type '{config.type}'")
    return notifiers[config.type](config.success, config.failure, config.subject, config.subject_failure, custom=config.custom, **config.params)

def make_db(name: str, config: cdatabase, providers: Dict[str, Provider], metadbs: Dict[str, MetaDB], connect: bool=True):
    try:
        prov = make_provider(name, config, providers)
    except Exception as e:
        raise KmVizConfigError(f"Error during '{name}' provider init: \"{e}\"")

    try:
        meta = make_metadb(config.metadata, metadbs)
    except Exception as e:
        raise KmVizConfigError(f"Error during '{name}' metadb init: \"{e}\"")

    prov.attach_metadata(meta)

    if connect:
        prov.db.connect()
        prov.connect()

    return prov


class ckmviz(BaseModel):
    idx: str = Field(kmviz_idx, frozen=True)
    databases: Dict[str, cdatabase]
    notif: Optional[cnotif]=None
    input: Optional[cinput]=cinput()
    default: cdefault = Field(cdefault(), alias="defaults")
    cache: Optional[ccache]=ccache()
    auth: Optional[Union[List[str], Dict[str, str]]]=None
    html: Optional[chtml]=chtml()
    api: Optional[capi]=capi()
    plugins: Optional[Dict[str, Dict[str, Any]]]={}
    assets: Optional[List[str]]=[]
    preset: Optional[Literal["flex", "fixed"]]="flex"
    ui: Optional[cui]=cui()

    _builtin_providers: Dict[str, Provider] = PrivateAttr(PROVIDERS.copy())
    _builtin_metadbs: Dict[str, Provider] = PrivateAttr(METADBS.copy())

    external_css: List[Union[Dict[str, Any], str]] = Field([], exclude=True)
    external_js: List[Union[Dict[str, Any], str]] = Field([], exclude=True)

    providers: Dict[str, Provider] = Field(PROVIDERS.copy(), exclude=True)
    metadbs: Dict[str, MetaDB] = Field(METADBS.copy(), exclude=True)
    notifiers: Dict[str, Notifier] = Field(NOTIFIERS.copy(), exclude=True)

    engine: Providers = Field(Providers(), exclude=True)
    notifier: Notifier = Field(NullNotifier(), exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("assets", mode="after")
    @classmethod
    def init_custom_assets(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        copy_custom_assets(value)
        return value

    @field_validator("plugins", mode="after")
    @classmethod
    def init_plugins(cls, value: Optional[Dict[str, Dict[str, Any]]]) -> Optional[Dict[str, Dict[str, Any]]]:
        if value is None:
            return value

        installed = installed_plugins()
        res = {}
        for name, params in value.items():
            if not name.startswith("kmviz_"):
                raise ValueError(f"'{name}' is not a valid plugin name")
            if name not in installed:
                raise ValueError(f"'{name}' is not installed")

            kmv_info(f"💾 Init[{name}]: with {list(params.keys())}")
            plugin = search_for_plugin(name)
            plugin.configure(params)

            res[name] = plugin
            if path := copy_plugin_assets(name):
                kmv_info(f"💾 Assets[{name}]: from '{path}'")
        return res

    @model_validator(mode="after")
    def post_init_plugins(self) -> Self:
        for name, plugin in self.plugins.items():
            ps, ds, ns = [], [], []
            for pname, p in plugin.providers():
                if pname not in self.providers:
                    ps.append(pname)
                    self.providers[pname] = p
            for dname, d in plugin.databases():
                if dname not in self.metadbs:
                    ds.append(dname)
                    self.metadbs[dname] = d
            for nname, n in plugin.notifiers():
                if nname not in self.notifiers:
                    ns.append(nname)
                    self.notifiers[nname] = n

            kmv_info(f"💾 Provider[{name}]: include {ps}")
            kmv_info(f"💾 MetaDB[{name}]: include {ds}")
            kmv_info(f"💾 Notifier[{name}]: include {ns}")

            if styles := plugin.external_styles():
                self.external_css.extend(styles)
                kmv_info(f"💾 CSS[{name}]: include {styles}")
            if scripts := plugin.external_scripts():
                self.external_js.extend(scripts)
                kmv_info(f"💾 JS[{name}]: include {scripts}")

        return self

    @model_validator(mode="after")
    def init_databases(self) -> Self:
        for db_name in self.databases.keys():
            kmv_info(f"📖 Init[{db_name}]: with type '{self.databases[db_name].type}'")
            db = make_db(db_name, self.databases[db_name], self.providers, self.metadbs, True)
            self.engine.add(db)
        return self

    @model_validator(mode="after")
    def init_notifiers(self) -> Self:
        if self.notif:
            kmv_info(f"📖 Init[Notifier]: with type '{self.notif.type}'")
            self.notifier = make_notif(self.notif, self.notifiers)
        return self


@dataclass
class _wrap_cache:
    server: Any
    manager: Any

@dataclass
class _wrap_caches:
    cache: _wrap_cache

class state:
    def __init__(self, mode: Optional[str]="db", config: Optional[Union[dict, str]]=None):
        self._init = config
        self._mode: str=mode
        self._config: ckmviz=None

        if self._init:
            self.configure(self._init)

    def configure(self, mode: str, config: Union[dict, str], rethrow=False):
        try:
            self._init = config
            self._mode = mode
            if mode == "db":
                self._config = ckmviz(**parse_config(config))
            else:
                self._config = ckmviz(databases={})
        except Exception as e:
            if rethrow:
                raise e
            kmv_error(e)
            exit(1)

    @cached_property
    def instance_plugin(self) -> Tuple[Optional[str], Optional[Any]]:
        if not self._config.plugins:
            return "/dashboard", None

        for name, p in self._config.plugins.items():
            if p.is_instance_plugin():
                if "dashboard" in p.config and p.config["dashboard"] != "/":
                    return p.config["dashboard"], p
                else:
                    return "/dashboard", p
        return "/dashboard", None

    def init_plugins_api(self, app):
        if not self.api.enabled:
            return
        apis = []
        for name, p in self._config.plugins.items():
            if p.has_api():
                apis.append(name)
                p.set_api(app)
        if apis:
            kmv_info(f"Load APIs from: [{','.join(apis)}]")

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def auth(self) -> Optional[Union[List[str], Dict[str, str]]]:
        return self._config.auth

    @property
    def caches(self) -> ccache:
        return self._config.cache

    @property
    def cache(self) -> KmvizResultCache:
        return self._config.cache.result

    def put(self, idx: str, value: Any):
        self.cache.put(idx, value)

    def get(self, idx: str) -> Any:
        return self.cache.get(idx)

    @property
    def limits(self) -> cinput:
        return self._config.input

    @property
    def api(self) -> capi:
        return self._config.api

    @property
    def html(self) -> chtml:
        return self._config.html

    @property
    def defaults(self) -> cdefault:
        return self._config.default

    @property
    def ui(self) -> cui:
        return self._config.ui

    @property
    def databases(self) -> Providers:
        return self._config.engine

    @property
    def css(self) -> List[Union[Dict[str, Any], str]]:
        return self._config.external_css

    @property
    def js(self) ->  List[Union[Dict[str, Any], str]]:
        return self._config.external_js

    def database(self, name: str) -> Provider:
        return self._config.engine.get(name)

    @property
    def engine(self) -> Providers:
        return self._config.engine

    @property
    def notif(self) -> Notifier:
        return self._config.notifier

    @property
    def db_list(self) -> List[str]:
        return self._config.engine.list()

    def db_query(self, query: Query, actives: List[str], options: Dict[str, Any], idx: str) -> Dict[str, QueryResponse]:
        return self._config.engine.query(query, actives, options, idx)

    @property
    def conf(self) -> ckmviz:
        return self._config

def init_global_state():
    global st
    st = state()
