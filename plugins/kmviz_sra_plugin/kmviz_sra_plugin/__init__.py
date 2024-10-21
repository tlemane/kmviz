from typing import Any
from kmviz.core.plugin import KmVizPlugin
from kmviz.core.provider.kmindex import KmindexProvider
from kmviz.core.query import Query, QueryResponse, Response
import pandas as pd
from kmviz.core.utils import make_cmd, exec_cmd
from kmviz.core.provider.options import MultiChoiceOption
import os

from typing import List, Tuple, Any
from pathlib import Path
import tempfile
import orjson

class KmindexSRAProvider(KmindexProvider):
    def __init__(self, name: str, blob_query_path: str, query_script: str, group_dict: str, group_stat: str, fp_file: str = ""):
        super().__init__(name)
        self._tmp = tempfile.mkdtemp()
        self._query_path = blob_query_path
        self._query_script = query_script
        self._query_cmd = self._query_script + " --list_groups {groups} --query_output " + self._query_path + " {idx} " + "--query {fastx}"
        self._group_stat = group_stat
        self._group_dict = group_dict
        self._fp_file = fp_file

        self._groups = {}

        with open(self._group_dict) as stream:
            self._groups = orjson.load(stream)

        self._stats = pd.read_csv(self._group_stat, sep="\t")

        self.options = {
          "groups": MultiChoiceOption(list(self._groups.keys()))
        }

    def has_abs(self) -> bool:
        return False

    def kmer_size(self) -> int:
        return 25

    def _make_kmindex_query_cmd(self, **arguments):
        return self._query_script.format(**arguments)

    def _execute(self, cmd: str, dir: str, **options):
        return exec_cmd(cmd, directory=dir, **options)

    def _get_tmp_paths(self, idx: str, query: Query):
        p = f"{self._tmp.name}/{idx}-{query.name}"
        return p, p + ".fa", p + "-groups.txt"

    def _make_groups(self, path: str, groups: list):
        with open(path, "w") as stream:
            if len(groups) == 0 or (len(groups) == 1 and groups[0] == "all"):
                for g in self._groups.values():
                    for x in g:
                        stream.write(f"{x}\n")
            else:
                for g in groups:
                    for x in self._groups[g]:
                        stream.write(f"{x}\n")

    def _make_kmindex_query(self, query: Query, options, idx) -> str:
        output, fastx, groups = self._get_tmp_paths(idx, query)

        self._make_groups(self, groups, options["groups"].value)

        with open(fastx, "w") as stream:
            stream.write(f">{query.name}\n")
            stream.write(f"{query.seq}\n")

        print(query.name)
        print(query.seq)

        cmd = self._make_kmindex_query_cmd(fastx=fastx, idx=idx, groups=groups)
        print(cmd)

        wd = os.makedirs(output + "/nf");

        #self._execute(cmd, wd)

        response = {"SRA": {}}

        for p in Path(self._result_path.format(idx=idx)).rglob('*.json'):
            with open(p) as jin:
                I = str(p).split("/")[-1].split(".")[0]
                R = orjson.loads(jin.read())[I]
                response["AZURE"].update(R[query.name])

        res = self._from_json(query, response)

        return res

    def connect(self):
        self.index_infos = (dict(a="TODO"))
        #self.index_infos = orjson.loads(self._execute(self._make_kmindex_infos_cmd(), capture=True))["index"]

    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:
        return self._make_kmindex_query(query, options, idx)

    def _from_json(self, query: Query, rj) -> QueryResponse:

        responses = {}
        for k, v in rj["SRA"].items():
            responses[k] = Response(self.kmer_size() + 5, float(v), None, None, None, None, None, None, None)

        data = { 'ID' : list(responses.keys()) }
        metadata = pd.DataFrame(data)

        covxks = []
        for r in metadata["ID"]:
            covxks.append(round(responses[r].xk, 3))

        metadata.insert(1, "CovXK", covxks, True)


        return QueryResponse(
            query,
            responses,
            metadata
        )

class SRAPlugin(KmVizPlugin):
    def name(self) -> str:
        return "SRAPlugin"

    def providers(self):
        return [("kmindex-sra", KmindexSRAProvider)]


kmviz_plugin = SRAPlugin()