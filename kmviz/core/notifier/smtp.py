from kmviz.core.notifier.notifier import Notifier, is_email
from kmviz.core.query.query import Query
from kmviz.core.provider.options import TextOption, update_option
from kmviz.core import KmVizQueryError

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

class SMTPNotifier(Notifier):
    def __init__(self,  success: str, failure: str, subject: str, subject_failure: str, server: str, sender: str, user: str, password: str, custom = {}):
        super().__init__(success, failure, subject, subject_failure, custom)
        self._server = server
        self._sender = sender
        self._client = SMTP(self._server)
        self._client.login(user, password)

    def send_success(self, session: str, options: dict, results: dict = {}):
        m = MIMEText(self.format_success(session), "text")
        m["Subject"] = self.format_subject(session)
        m["From"] = self._sender
        return self._client.sendmail(self._sender, options["Email"], m.as_string())

    def send_failure(self, session: str, options: dict, reason: str = None):
        m = MIMEText(self.format_failure(session, reason), "text")
        m["Subject"] = self.format_subject_failure(session, reason)
        m["From"] = self._sender
        return self._client.sendmail(self._sender, options["Email"], m.as_string())

    def check(self, options: dict):
        if not is_email(options["Email"]):
            raise KmVizQueryError(f"'{options['Email']}': not an email.")

    def options(self):
        return {"Email": update_option(TextOption("Email", "", "Your email"), {"is_required": True})}




