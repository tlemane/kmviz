from .provider import Providers, Provider
from .kmindex import KmindexServerProvider, KmindexCLIProvider

PROVIDERS = {
    "kmindex-server": KmindexServerProvider,
    "kmindex-cli": KmindexCLIProvider
}
