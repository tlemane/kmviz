from dataclasses import dataclass
from typing import Union, Iterable, Any, Optional

from kmviz.core import KmVizError

class InvalidOptionValue(KmVizError):
    pass

@dataclass
class ProviderOption:
    name: str
    default: Any

    def __post_init__(self):
        if self.value is None:
            self.value = self.default

    @property
    def hidden(self):
        if hasattr(self, "is_hidden"):
            return self.is_hidden
        return False

    @property
    def required(self):
        if hasattr(self, "is_required"):
            return self.is_required
        return False

@dataclass
class NumericOption(ProviderOption):
    min: Optional[Union[int, float]]
    max: Optional[Union[int, float]]
    step: Optional[Union[int, float]]
    value: Union[int, float] = None

@dataclass
class ChoiceOption(ProviderOption):
    choices: Iterable[Union[str, int, float]]
    value: Union[str, int, float] = None

@dataclass
class MultiChoiceOption(ProviderOption):
    choices: Iterable[Union[str, int, float]]
    value: Iterable[Union[str, int, float]] = None

@dataclass
class RangeOption(ProviderOption):
    min: Union[int, float]
    max: Union[int, float]
    step: Union[int, float]
    value: Union[int, float] = None

@dataclass
class TextOption(ProviderOption):
    placeholder: str = None
    value: str = None

def update_option(opt, d):
    for k, v in d.items():
        if hasattr(opt, k):
            setattr(opt, k, v)
        elif (k == "hide"):
            opt.is_hidden = bool(v)
    return opt
