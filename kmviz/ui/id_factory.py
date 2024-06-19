from dash import Patch, ALL, MATCH
from typing import Any, List, Tuple, Union

class IDFactory:
    def __init__(self, *prefixes) -> None:
        self._prefix = "-".join(prefixes)
        self._index = 0
        self._order = 0
        self._iid_register = set()
        self._sid_register = set()
        self._children = []

    def _iid(self, index: Any) -> dict:
        if index is None:
            res = { "type": self._prefix, "index": self._index}
            self._index += 1
        else:
            res = { "type": self._prefix, "index": index}

        self._iid_register.add((res["type"], res["index"], self._order))
        self._order += 1
        return res

    def sid(self, id: str) -> str:
        res = f"{self._prefix}-{id}"
        self._sid_register.add(res)
        return res

    def iid(self, index: Any=None) -> dict:
        return self._iid(index)

    def __call__(self, index: Any=None) -> dict:
        return self.iid(index)

    def child(self, suffix: str) -> "IDFactory":
        self._children.append(IDFactory(self._prefix, suffix))
        return self._children[-1]

    def list(self) -> Tuple[List[str], List[dict]]:
        return list(self._sid_register), list(self._iid_register)

    def list_all(self) -> Tuple[List[str], List[dict]]:
        sid, idd = self.list()
        for c in self._children:
            c_sid, c_iid = c.list_all()
            sid.extend(c_sid), idd.extend(c_iid)
        return sid, idd

    @property
    def type(self):
        return self._prefix

    @property
    def all(self):
        return {"type": self._prefix, "index": ALL}

kmviz_factory = IDFactory("kmviz")
kmviz_store_factory = kmviz_factory.child("store")
