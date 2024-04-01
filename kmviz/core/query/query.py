import pandas as pd
from enum import Enum
from typing import List, Union, Iterable, Dict, Any
from dataclasses import dataclass

from kmviz.core import KmVizError

@dataclass
class Query:
    _name: str
    _seq: str

    @property
    def name(self) -> str:
        return self._name

    @property
    def seq(self) -> str:
        return self._seq

@dataclass
class Response:
    _k: int
    _xk: float = None
    _yk: int = None
    _covxk: List[int] = None
    _covyk: List[int] = None
    _xb: float = None
    _yb: int = None
    _covxb: List[int] = None
    _covyb: List[int] = None
    _extra: Any = None

    @property
    def k(self) -> int:
        return self._k

    @property
    def xk(self) -> float:
        return self._xk

    @property
    def yk(self) -> float:
        return self._yk

    @property
    def xb(self) -> float:
        return self._xb

    @property
    def yb(self) -> float:
        return self._yb

    @property
    def covxk(self) -> List[int]:
        return self._covxk

    @property
    def covyk(self) -> List[int]:
        return self._covyk

    @property
    def covxb(self) -> List[int]:
        return self._covxb

    @property
    def covyb(self) -> List[int]:
        return self._covyb

    @property
    def extra(self) -> Any:
        return self._extra

    def has_abs(self) -> bool:
        return bool(self.yk) or bool(self.yb)


@dataclass
class QueryResponse:
    _query: Query
    _response: Dict[str, Response]
    _metadata: pd.DataFrame

    @property
    def query(self) -> Query:
        return self._query

    @property
    def response(self) -> Dict[str, Response]:
        return self._response

    @property
    def name(self) -> str:
        return self.query.name

    @property
    def sequence(self) -> str:
        return self.query.sequence

    @property
    def df(self) -> str:
        return self._metadata

