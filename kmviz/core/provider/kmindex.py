import uplink
import json
import pandas as pd
import orjson
import tempfile
import shutil
from typing import Optional, Union, List
from .provider import Provider
from .options import RangeOption
from kmviz.core.query import Query, Response, QueryResponse
from kmviz.core.utils import covxb_from_covxk, covyb_from_covyk, make_cmd, exec_cmd
from kmviz.core.io import rm

class KmindexProvider(Provider):
    def __init__(self, name: str):
        super().__init__(name)

        self.options = {
            "z": RangeOption("z", 0, min=0, max=5, step=1),
            "coverage": RangeOption("coverage", 0.1, min=0.0, max=1.0, step=0.05),
        }

    def has_abs(self) -> bool:
        return self.index_infos[list(self.index_infos.keys())[0]]["bw"] > 1

    def kmer_size(self) -> int:
        smer_size = self.index_infos[list(self.index_infos.keys())[0]]["smer_size"]
        return smer_size

    def samples(self, index=None):
        if index:
            return self.index_infos[index]
        else:
            res = {}
            for k, v in self.index_infos.items():
                res[k] = v["Samples"]
            return res

    def index_list(self) -> List[str]:
        return list(self.index_infos.keys())

    @property
    def infos_df(self) -> pd.DataFrame:
        key = list(self.infos().keys())[0]
        cols = ["index"] + list(self.infos()[key].keys())
        cols.remove("samples")

        df = pd.DataFrame(columns=cols)
        for k, v in self.infos().items():
            v["index"] = k
            df.loc[len(df)] = v

        return df

    def _response_from_dict(self, response: dict, size: int, z: int) -> Response:
        if self.has_abs():
            return self._response_from_dict_abs(response, size, z)
        else:
            return self._response_from_dict_pa(response, size, z)

    def _response_from_dict_pa(self, response: dict, size: int, z) -> Response:
        xk = response["R"]
        covxk = response["P"]

        xb, covxb = covxb_from_covxk(covxk, self.kmer_size() + z, size)

        return Response(
            self.kmer_size() + z,
            xk,
            None,
            covxk,
            None,
            xb,
            None,
            covxb,
            None
        )

    def _response_from_dict_abs(self, response: dict, size: int, z: int) -> Response:
        covyk = response["P"]
        xk = response["R"]

        yk, xb, yb, covyb = covyb_from_covyk(covyk, self.kmer_size() + z, size)

        return Response(
            self.kmer_size() + z,
            xk,
            yk,
            None,
            covyk,
            xb,
            yb,
            None,
            covyb,
        )

    def _from_json(self, query: Query, options, rj) -> QueryResponse:
        responses = {}
        for k, v in rj.items():
            for qid, results in v.items():
                for sample, d in results.items():
                    responses[sample] = self._response_from_dict(d, len(query.seq), options["z"].value)

        metadata = self.db.query(responses.keys())

        covxks = []
        covxbs = []
        covyks = []
        covybs = []

        for r in metadata["ID"]:
            covxks.append(round(responses[r].xk, 3))
            covxbs.append(round(responses[r].xb, 3))

            if self.has_abs():
                covyks.append(round(responses[r].yk, 3))
                covybs.append(round(responses[r].yb, 3))

        metadata.insert(1, "CovXK", covxks, True)
        metadata.insert(2, "CovXB", covxbs, True)

        if self.has_abs():
            metadata.insert(3, "CovYK", covyks , True)
            metadata.insert(4, "CovYB", covybs, True)

        return QueryResponse(
            query,
            responses,
            metadata
        )

class KmindexCLIProvider(KmindexProvider):
    def __init__(self, name: str, index_path: str, executable: Optional[str]=None):
        super().__init__(name)
        self._bin = executable if executable else "kmindex"
        self._index_path = index_path
        self._tmp = tempfile.TemporaryDirectory()

    def _make_kmindex_infos_cmd(self):
        return make_cmd(self._bin, "index-infos", "--", index=self._index_path)

    def _make_kmindex_query_cmd(self, **arguments):
        return make_cmd(self._bin, "query", "--", index=self._index_path, verbose="error", **arguments)

    def _execute(self, cmd: str, **options):
        return exec_cmd(cmd, **options)

    def _get_tmp_paths(self, idx: str, query: Query):
        p = f"{self._tmp.name}/{idx}-{query.name}"
        return p, p + ".fa"

    def _make_options(self, fastx, output, options):
        kwargs = {}
        kwargs["fastx"] = fastx
        kwargs["output"] = output
        kwargs["zvalue"] = options["z"].value
        kwargs["threshold"] = options["coverage"].value
        kwargs["format"] = "json_vec"
        kwargs["aggregate"] = None
        kwargs["fast"] = None
        return kwargs

    def _make_kmindex_query(self, query: Query, options, idx) -> str:
        output, fastx = self._get_tmp_paths(idx, query)

        with open(fastx, "w") as stream:
            stream.write(f">{query.name}\n")
            stream.write(f"{query.seq}\n")

        kwargs = self._make_options(fastx, output, options)
        cmd = self._make_kmindex_query_cmd(**kwargs)
        self._execute(cmd)

        response = {}
        for i in self.index_list():
            with open(f"{output}/{i}.json") as jin:
                response[i] = orjson.loads(jin.read())[i]

        res = self._from_json(query, options, response)

        rm(fastx, output)

        return res

    def connect(self):
        self.index_infos = orjson.loads(self._execute(self._make_kmindex_infos_cmd(), capture=True))["index"]

    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:
        return self._make_kmindex_query(query, options, idx)

class KmindexServerProvider(KmindexProvider):

    class KMIndexAPI(uplink.Consumer):
        @uplink.get("kmindex/infos")
        def infos(self):
            "Fetches indexes information."

        @uplink.json
        @uplink.post("kmindex/query")
        def query(self, data: uplink.Body):
            "Query indexes."

    def __init__(self, name: str, url: str, port: int) -> None:
        super().__init__(name)
        self._url = url
        self._port = port
        self._api = self.KMIndexAPI(base_url=f"http://{self._url}:{self._port}")

    def connect(self):
        self.index_infos = dict(self._api.infos().json())["index"]

    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:

        if len(query.seq) < self.kmer_size():
            return f"min sequence size is {self.kmer_size()}"

        response = self._api.query(self.make_payload(query, options))

        return self._from_json(query, options, response.json())

    def make_payload(self, query: Query, options) -> json:
        wrap = lambda x: [x] if isinstance(x, str) else x
        return {
            "id": query.name,
            "seq": wrap(query.seq),
            "index": self.index_list(),
            "r": options["coverage"].value,
            "z": options["z"].value,
            "format": "json_vec"
        }





