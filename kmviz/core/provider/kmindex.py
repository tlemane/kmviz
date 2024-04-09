import uplink
import json
import pandas as pd

from typing import Optional, Union, List

from .provider import Provider
from .options import RangeOption
from kmviz.core.query import Query, Response, QueryResponse
from kmviz.core.utils import covxb_from_covxk, covyb_from_covyk
from kmviz.core.io import KmVizInvalidQuery
from statistics import mean

import json

class KmindexProvider(Provider):
    pass

class KmindexServerProvider(KmindexProvider):

    class KMIndexAPI(uplink.Consumer):
        @uplink.get("kmindex/infos")
        def infos(self):
            "Fetches indexes informations."

        @uplink.json
        @uplink.post("kmindex/query")
        def query(self, data: uplink.Body):
            "Query indexes."

    def __init__(self, name: str, url: str, port: int) -> None:
        super().__init__(name)
        self._url = url
        self._port = port
        self._api = self.KMIndexAPI(base_url=f"http://{self._url}:{self._port}")

        self.options = {
            "z": RangeOption("z", 0, min=0, max=5, step=1),
            "coverage": RangeOption("coverage", 0.7, min=0.0, max=1.0, step=0.05)
        }

    def connect(self):
        self.index_infos = dict(self._api.infos().json())["index"]

    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:

        if len(query.seq) < self.kmer_size():
            return f"min sequence size is {self.kmer_size()}"

        response = self._api.query(self.make_payload(query, options))

        rj = response.json()

        responses = {}
        for k, v in rj.items():
            for qid, results in v.items():
                for sample, d in results.items():
                    responses[sample] = self._response_from_dict(d, len(query.seq))

        metadata = self.db.query(responses.keys())

        covxks = []
        covxbs = []

        for r in responses.values():
            covxks.append(round(r.xk, 3))
            covxbs.append(round(r.xb, 3))

        metadata.insert(1, "CovXK", covxks, True)
        metadata.insert(2, "CovXB", covxbs, True)

        if self.has_abs():
            covyks = []
            covybs = []

            for r in responses.values():
                covyks.append(round(r.yk, 3))
                covybs.append(round(r.yb, 3))


            metadata.insert(3, "CovYK", covyks , True)
            metadata.insert(4, "CovYB", covybs, True)

        return QueryResponse(
            query,
            responses,
            metadata
        )


    def _response_from_dict(self, response: dict, size: int) -> Response:
        if self.has_abs():
            return self._response_from_dict_abs(response, size)
        else:
            return self._response_from_dict_pa(response, size)

    def _response_from_dict_pa(self, response: dict, size: int) -> Response:
        xk = response["R"]
        covxk = response["P"]

        xb, covxb = covxb_from_covxk(covxk, self.kmer_size(), size)

        return Response(
            self.kmer_size(),
            xk,
            None,
            covxk,
            None,
            xb,
            None,
            covxb,
            None
        )

    def _response_from_dict_abs(self, response: dict, size: int) -> Response:
        covyk = response["P"]
        xk = response["R"]

        yk, xb, yb, covyb = covyb_from_covyk(covyk, self.kmer_size(), size)

        return Response(
            self.kmer_size(),
            xk,
            yk,
            None,
            covyk,
            xb,
            yb,
            None,
            covyb,
        )

    def has_abs(self) -> bool:
        return self.index_infos[list(self.index_infos.keys())[0]]["bw"] > 1

    def kmer_size(self) -> int:
        smer_size = self.index_infos[list(self.index_infos.keys())[0]]["smer_size"]
        return self.options["z"].value + smer_size

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




