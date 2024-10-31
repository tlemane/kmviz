from abc import ABC, abstractmethod
from kmviz.core.query import Query
from kmviz.core.log import kmv_info, kmv_warn
from kmviz.core.provider.options import TextOption

class Notifier(ABC):
    def __init__(self, success: str, failure: str, subject: str, subject_failure: str, custom: dict = {}):
        self._success = success
        self._failure = failure
        self._subject = subject
        self._subject_failure = subject_failure
        self._custom = custom

    @abstractmethod
    def send_success(self, session: str, options: dict, results: dict = {}):
        """
        Send success notification
        """

    @abstractmethod
    def send_failure(self, session: str, options: dict, reason: str = None):
        """
        Send failure notification
        """

    def check(self, options: dict):
        pass

    def format_success(self, session: str, **kwargs):
        return self._success.format(SESSION=session, **kwargs, **self._custom)

    def format_failure(self, session: str, reason: str, **kwargs):
        return self._failure.format(SESSION=session, REASON=reason, **kwargs, **self._custom)

    def format_subject(self, session: str, **kwargs):
        return self._subject.format(SESSION=session, **kwargs, **self._custom)

    def format_subject_failure(self, session: str, reason: str, **kwargs):
        return self._subject_failure.format(SESSION=session, REASON=reason, **kwargs, **self._custom)

    def options(self):
        return {}

class NullNotifier(Notifier):
    def __init__(self):
        super().__init__("", "", "", "")

    def send_success(self, query: Query, session: str, options: dict):
        kmv_info(f"[notif-success] {session}")

    def send_failure(self, query: Query, session: str, options: dict, reason: str = None):
        kmv_warn(f"[notif-failure] {session} (reason: {str(reason)})")


import re

def is_email(s: str):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', s)