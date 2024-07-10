from kmviz.ui import state
from kmviz.core.io import parse_fastx, KmVizIOError
from kmviz.core.query import Query, QueryResponseGeo

from flask import jsonify
from flask import request
import orjson
import uuid
import base64

import dataclasses

def api_root():
    res = {}

    for name, provider in state.kmstate.providers.all().items():
        options = list(provider.options.keys())
        res[name] = {}

        options = {}
        for opt_name, opt in provider.options.items():
            options[opt_name] = {
                "type": type(opt.default).__name__,
                "state": dataclasses.asdict(opt)
            }
        res[name]["options"] = options

    return jsonify(res)

def make_query(fastx, on):
    uuid_str = f"kmviz-{str(uuid.uuid4())}"

    queries = [Query(name, seq) for name, seq, _ in parse_fastx(fastx, state.kmstate.api_config["limits"])]

    results = {}

    for provider in list(on.keys()):
        for k, v in state.kmstate.providers.get(provider).options.items():
            if k not in on[provider]:
                on[provider][k] = v.value
            else:
                on[provider][k] = type(v.value)(on[provider][k])

    for i, query in enumerate(queries):
        result = state.kmstate.providers.query(query, list(on.keys()), on, uuid_str)

        for name in result:
            R = QueryResponseGeo(
                result[name]._query,
                result[name]._response,
                orjson.loads(result[name].df.to_json()),
                state.kmstate.providers.get(name).db.geodata
            )
            result[name] = R

        results[query.name] = result

    return results

def api_query():
    try:
        if not "database" in request.form:
            return f"'database' entry is missing!", 400
        if not "fastx" in request.files:
            return f"'fastx' entry is missing!", 400

        options = {}
        for db in request.form.getlist("database"):
            if db not in state.kmstate.providers.list():
                return f"'{db}' is not a valid database", 400
            options[db] = {}
            for k in request.form:
                if k.startswith(db):
                    name = k.split("-", 1)[1]
                    if name not in state.kmstate.providers.get(db).options:
                        return f"'{name}' is not a valid option for '{db}'"
                    options[db][name] = request.form[k]


        res = make_query(request.files["fastx"].stream.read().decode(), options)
        return jsonify(res)
    except KmVizIOError as e:
        return f"Error: {str(e)}", 400
    except:
        return "An error occured while processing your request", 400


def register_api_routes(server):
    if state.kmstate.api:
        root = state.kmstate.api_config["route"]
        server.route(root, methods=["POST", "GET"])(api_root)
        server.route(root + state.kmstate.api_config["query_route"], methods=["POST"])(api_query)