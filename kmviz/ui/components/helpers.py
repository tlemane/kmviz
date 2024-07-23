import base64
from io import StringIO, BytesIO

from typing import Union, Optional
from pathlib import Path

import pandas as pd

from kmviz.core.io import KmVizIOError

import orjson

def load_file_content(filename, contents, decode: Optional[str]=None) -> Union[str, bytes]:
    content_type, data = contents.split(",")
    content = base64.b64decode(data)

    if decode:
        return content.decode(decode)

    return content

def load_file_as_df(filename, contents, sep: Optional[str]=",") -> pd.DataFrame:
    data = load_file_content(filename, contents)

    filename = Path(filename)

    try:
        if filename.suffix in (".csv", ".tsv"):
            dio = StringIO(data.decode("utf-8"))
            return pd.read_csv(dio, sep=sep)
        elif filename.suffix in (".xlsx"):
            dio = BytesIO(data)
            return pd.read_excel(dio)
    except Exception as e:
        raise KmVizIOError(f"Error while loading '{filename}' [{str(e)}]")

    raise KmVizIOError(f"'{filename.suffix}' files are not supported")

def magic_json(d: dict):
    c = d.copy()
    for k, v in d.items():
        if "_" in k:
            sk, sv = k.split("_", 1)
            if sk not in c:
                c[sk] = {}
            if isinstance(v, dict):
                v = magic_json(v)
            c[sk][sv] = v
            c[sk] = magic_json(c[sk])
            del c[k]
    return c

def from_json(value, p=None):
    try:
        value = orjson.loads(value)
        if p:
            value = value[p]
        return value
    except:
        return None

def from_json_list(value, p=None):
    try:
        value = orjson.loads(value)
        if isinstance(value, list):
            return value
        if p:
            value = value[p]
        return value
    except:
        return None

