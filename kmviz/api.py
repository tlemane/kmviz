from kmviz.core.config import state
from kmviz.core.io import parse_fastx, KmVizIOError
from kmviz.core.query import Query, QueryResponseGeo
from kmviz.core.log import kmv_info, kmv_warn
from flask import jsonify, send_file
from flask import request
import orjson
import uuid
import dataclasses
from io import StringIO, BytesIO
from zipfile import ZipFile

from typing import List

class KmvizAPI:
    def __init__(self, st: state, server):
        self.st = st
        self.server = server
        self._register()

    def _register(self):
        if self.st.api.enabled:
            if self.st.api.with_query:
                self._register_route(f"{self.st.api.route}{self.st.api.query_route}", ["POST"], self._make_query_callback())
                self._register_route(f"{self.st.api.route}{self.st.api.query_route}/<db>", ["POST"], self._make_query_metadata_callback())
            if self.st.api.with_download:
                self._register_route(f"{self.st.api.route}{self.st.api.download_route}/<session>", ["GET", "POST"], self._make_download_callback())


    def _get_options(self, database, form, with_prefix = True):
        options = {}
        for key in form:
            if with_prefix:
                if key.startswith(database):
                    n = key.split("#", 1)[1]
                    if n not in self.st.engine.get(database).options:
                        raise KmVizIOError(f"'{n}' is not a valid option for '{database}'")
                    options[n] = form[key]
            else:
                if key not in self.st.engine.get(database).options:
                    raise KmVizIOError(f"'{key}' is not a valid option for '{database}'")
                options[key] = form[key]

        for opt_name, opt in self.st.engine.get(database).options.items():
            if opt_name not in options:
                options[opt_name] = opt.value
            else:
                options[opt_name] = type(opt.value)(options[opt_name])
        return options

    def _make_geo_response(self, response, db, df_as_json):
        return QueryResponseGeo(
            response._query,
            response._response,
            orjson.loads(response.df.to_json()) if df_as_json else response.df,
            self.st.engine.get(db).db.geodata
        )

    def _make_session_query(self, fastx: str, options: dict, df_as_json):
        uuid_str = f"kmviz-{str(uuid.uuid4())}"

        queries = [Query(name, seq) for name, seq, _ in parse_fastx(fastx, self.st.api.limits)]

        results = {}
        stores = {}

        for i, query in enumerate(queries):
            result = self.st.engine.query(query, list(options.keys()), options, uuid_str)

            stores[query.name] = {}
            for name in result:
                stores[query.name][name] = result[name]
                result[name] = self._make_geo_response(result[name], name, df_as_json)

            results[query.name] = result

        data_db = list(options.keys())
        def_db = data_db[0]

        self.st.put(uuid_str, (stores, data_db, def_db, [q.name for q in queries], queries[0].name))
        return { uuid_str: results }

    def _make_query_callback(self):
        def api_query():
            try:
                if not "database" in request.form:
                    kmv_warn("🔗 API (POST): 'database' is missing")
                    return f"'database' entry is missing!", 400
                if not "fastx" in request.files:
                    kmv_warn("🔗 API (POST): 'fastx' is missing")
                    return f"'fastx' entry is missing!", 400

                options = {}
                for db in request.form.getlist("database"):
                    options[db] = self._get_options(db, request.form, True)

                return jsonify(self._make_session_query(request.files["fastx"].stream.read().decode(), options, True))
            except KmVizIOError as e:
                kmv_warn(f"🔗 API (POST): Error ({str(e)})")
                return f"Error: {str(e)}", 400
            except Exception as e:
                kmv_warn(f"🔗 API (POST): Unknown error: {str(e)}")
                return "An error occured while processing your request", 400
        return api_query

    def _make_metadata_query(self, fastx: str, options: dict):
        uuid_str = f"kmviz-{str(uuid.uuid4())}"

        queries = [Query(name, seq) for name, seq, _ in parse_fastx(fastx, self.st.api.limits)]

        zf_io = BytesIO()
        with ZipFile(zf_io, "w") as zf:
            stores = {}
            for i, query in enumerate(queries):
                result = self.st.engine.query(query, list(options.keys()), options, uuid_str)
                stores[query.name] = {}
                for name in result:
                    zf.writestr(f"{query.name}.tsv", result[name].df.to_csv(index=False, sep="\t"))
                    stores[query.name][name] = result[name]


        data_db = list(options.keys())
        def_db = data_db[0]
        self.st.put(uuid_str, (stores, data_db, def_db, [q.name for q in queries], queries[0].name))

        zf_io.seek(0)
        return send_file(zf_io, download_name=f"{uuid_str}.zip")

    def _make_query_metadata_callback(self):
        def api_metadata_query(db):
            try:
                if db not in self.st.engine.list():
                    return f"'{db}' database does not exist!", 400
                if not "fastx" in request.files:
                    kmv_warn("🔗 API (POST): 'fastx' is missing")
                    return f"'fastx' entry is missing!", 400
                options = {db: self._get_options(db, request.form, False)}
                return self._make_metadata_query(request.files["fastx"].stream.read().decode(), options)
            except KmVizIOError as e:
                kmv_warn(f"🔗 API (POST): Error ({str(e)})")
                return f"Error: {str(e)}", 400
            except Exception as e:
                kmv_warn(f"🔗 API (POST): Unknown error: {str(e)}")
                return "An error occured while processing your request", 400
        return api_metadata_query


    def _make_info_callback(self):
        def api_info():
            results = dict(database={})

            kmv_info("🔗 API (GET)[info]")

            for name, db in self.st.engine.all().items():
                results["database"] = { name: {}}

                options = {}
                for opt_name, opt in db.options.items():
                    options[opt_name] = {
                        "type": type(opt.default).__name__,
                        "state": dataclasses.asdict(opt)
                    }
                results["database"][name]["options"] = options

            results["input"] = self.st.api.limits.model_dump()

            return jsonify(results)

        return api_info

    def _make_download_result(self, session):
        res = self.st.get(session)[0]
        zf_io = BytesIO()
        results = {}
        with ZipFile(zf_io, "w") as zf:
            for query_name, result in res.items():
                for name in result:
                    zf.writestr(f"{query_name}.tsv", result[name].df.to_csv(index=False, sep="\t"))
                    result[name] = self._make_geo_response(result[name], name, True)
                results[query_name] = result
            zf.writestr("session.json", orjson.dumps(jsonify({session: results}).json).decode())
        zf_io.seek(0)
        return send_file(zf_io, download_name=f"{session}.zip")

    def _make_download_callback(self):
        def api_download(session):
            try:
                kmv_info("🔗 API (POST)[download]")
                return self._make_download_result(session)
            except KmVizIOError as e:
                kmv_warn(f"🔗 API (GET): Error ({str(e)})")
                return f"Error: {str(e)}", 400
            except Exception as e:
                kmv_warn(f"🔗 API (GET): Unknown error: {str(e)}")
                return "An error occured while processing your request", 400
        return api_download

    def _register_route(self, route: str, methods: List[str], callback):
        self.server.route(route, methods=methods)(callback)
