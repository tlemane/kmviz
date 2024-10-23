from typing import Any
from kmviz.core.plugin import KmVizPlugin
from kmviz.core.provider.kmindex import KmindexProvider
from kmviz.core.query import Query, QueryResponse, Response
import pandas as pd
from kmviz.core.utils import make_cmd, exec_cmd
from kmviz.core.provider.options import MultiChoiceOption, TextOption
import os
from flask import request
from typing import List, Tuple, Any
from pathlib import Path
import tempfile
import orjson
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dash import dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions.enrich import html
from kmviz.core import KmVizQueryError

content_template = """Dear user,

Your query '{QUERY}' over all Logan unitigs is complete.

Please visit '{URL}/api/download/{SESSION}' to download your results. You can also visit '{URL}/{SESSION}' to visualize them using our web interface.

Best regards,

The Logan/IndexThePlanet/kmindex teams

"""

content_template_failure = """Dear user,

Your query '{QUERY}' over all Logan unitigs failed. (session: {SESSION})
If the issue persists please contact us.

Best regards,

The Logan/IndexThePlanet/kmindex teams

"""

class Notifier:
    def __init__(self, key: str, sender: str, obj_prefix: str):
        self.key = key
        self.sender = sender
        self.obj_prefix = obj_prefix
        self.client = sendgrid.SendGridAPIClient(api_key=self.key)

    def send(self, idx, query_name, to):
        c = Content("text/plain", content_template.format(QUERY=query_name, URL=request.host_url, SESSION=idx))
        m = Mail(Email(self.sender), To(to), f"{self.obj_prefix} {idx}", c)
        self.client.client.mail.send.post(request_body=m.get())

    def send_failure(self, idx, query_name, to):
        c = Content("text/plain", content_template_failure.format(QUERY=query_name, SESSION=idx))
        m = Mail(Email(self.sender), To(to), f"{self.obj_prefix} {idx}", c)
        self.client.client.mail.send.post(request_body=m.get())

import re

class KmindexSRAProvider(KmindexProvider):
    def __init__(self,
                 name: str,
                 blob_query_path: str,
                 blob_prefix: str,
                 query_script: str,
                 group_dict: str,
                 group_stat: str,
                 notif_apikey: str,
                 notif_sender: str,
                 notif_obj: str,
                 fp_file: str = ""):
        super().__init__(name)
        self._tmp = tempfile.mkdtemp()
        self._query_path = blob_query_path
        self._blob_prefix = blob_prefix
        self._query_script = query_script
        self._query_cmd = self._query_script + " --list_groups {groups} --query_output " + self._query_path + "/{idx} " + "--query {fastx}"
        self._group_stat = group_stat
        self._group_dict = group_dict
        self._fp_file = fp_file

        self._groups = {}

        with open(self._group_dict) as stream:
            self._groups = orjson.loads(stream.read())

        self._stats = pd.read_csv(self._group_stat, sep=" ")

        self.options = {
          "groups": MultiChoiceOption(name="groups", default=[], choices=["all"] + list(self._groups.keys()), required=True),
          "mail": TextOption(name="mail", default=None, placeholder="Your email", required=True)
        }

        self.notif = Notifier(notif_apikey, notif_sender, notif_obj)

    def has_abs(self) -> bool:
        return False

    def kmer_size(self) -> int:
        return 25

    def _make_kmindex_query_cmd(self, **arguments):
        return self._query_cmd.format(**arguments)

    def _execute(self, cmd: str, dir: str, **options):
        return exec_cmd(cmd, directory=dir, **options)

    def _get_tmp_paths(self, idx: str, query: Query):
        p = f"{self._tmp}/{idx}-{query.name}"
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

        self._make_groups(groups, options["groups"].value)

        with open(fastx, "w") as stream:
            stream.write(f">{query.name}\n")
            stream.write(f"{query.seq}\n")

        cmd = self._make_kmindex_query_cmd(fastx=fastx, idx=idx, groups=groups)

        wd = os.makedirs(output + "-nf");
        self._execute(cmd, wd)

        response = {"SRA": {}}

        exec_cmd(f"ls {self._blob_prefix}/{self._query_path}", capture=False)
        for p in Path(f"{self._blob_prefix}/{self._query_path}/{idx}").rglob('*.json'):
            with open(p) as jin:
                I = str(p).split("/")[-1].split(".")[0]
                R = orjson.loads(jin.read())[I]
                response["SRA"].update(R[query.name])

        res = self._from_json(query, response)

        if len(options["mail"].value) > 1:
            self.notif.send(idx, query.name, options["mail"].value)

        return res

    def connect(self):
        self.index_infos = self._stats.to_dict()

    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:
        print(options["mail"].value)
        if not options["mail"].value:
            raise KmVizQueryError("email is mandatory.")
        else:
            v = options["mail"].value
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', options["mail"].value):
                raise KmVizQueryError(f"'{v}' not a valid email.")
        try:
            return self._make_kmindex_query(query, options, idx)
        except:
            self.notif.send_failure(idx, query.name, options["mail"].value)
            raise KmVizQueryError("Query failure. Please retry later")

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

    @property
    def infos_df(self) -> pd.DataFrame:
        return self._stats

class SRAPlugin(KmVizPlugin):
    def name(self) -> str:
        return "SRAPlugin"

    def is_instance_plugin(self) -> bool:
        return True

    def providers(self):
        return [("kmindex-sra", KmindexSRAProvider)]

    def instance(self) -> html.Div:
        layout = html.Div([
            dcc.Markdown("""
            ## Welcome to the kmviz Logan instance
            """),
            html.A(
                dmc.Button(
                    "Query the planet",
                    leftIcon=DashIconify(icon="noto:rocket", width=20),
                    style={"position":"fixed", "top": "30%", "left":"50%"}
                ),
                href="/dashboard"
            ),
        ])

        return layout

    def help(self):
        res = dcc.Markdown("""
            ### Logan documentation
        """
        )
        return res

kmviz_plugin = SRAPlugin()
