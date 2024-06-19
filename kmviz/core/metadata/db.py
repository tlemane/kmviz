from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd

class MetaDB(ABC):
    def __init__(self, idx: str, geodata: Dict[str, str] = {}) -> None:
        self._geodata = geodata
        self._idx = idx

    @abstractmethod
    def connect(self):
        """
        Initialization, like database login, should take place here
        """
        ...

    @abstractmethod
    def query(self, keys: List[str]) -> pd.DataFrame:
        """
        Select a subset of metadata

        :param keys: A sequence of identifiers
        :returns: A dataframe with the metadata corresponding to the keys
        """
        ...

    @abstractmethod
    def df(self) -> pd.DataFrame:
        """
        Get all metadata

        :returns: A dataframe with all metadata
        """
        ...

    @abstractmethod
    def keys(self) -> List[str]:
        """
        Get all fields

        :returns: The list of all fields
        """
        ...

    @property
    def geodata(self) -> dict:
        """
        :returns: A dict with the name of geographical data fields
        
        Ex:
        {
          "latitude": "Lat",
          "longitude": "Long"
        }
        """
        return self._geodata

    @property
    def idx(self) -> str:
        """
        :returns: The name of the field corresponding to entry identifiers
        """
        return self._idx




