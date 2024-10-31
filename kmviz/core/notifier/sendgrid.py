from kmviz.core.notifier.notifier import Notifier, is_email
from kmviz.core.query.query import Query
from kmviz.core import KmVizQueryError
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from kmviz.core.provider.options import TextOption, update_option
import re

class SendGridNotifier(Notifier):
    def __init__(self,  success: str, failure: str, subject: str, subject_failure: str, api_key: str, sender: str, custom = {}):
        super().__init__(success, failure, subject, subject_failure, custom)
        self._api = api_key
        self._sender = sender
        self._client = sendgrid.SendGridAPIClient(api_key=self._api)

    def send_success(self, session: str, options: dict, results: dict = {}):
        c = Content("text/plain", self.format_success(session))
        m = Mail(Email(self._sender), To(options["Email"]), self.format_subject(session), c)
        return self._client.client.mail.send.post(request_body=m.get())

    def send_failure(self, session: str, options: dict, reason: str = None):
        c = Content("text/plain", self.format_failure(session, reason))
        m = Mail(Email(self._sender), To(options["Email"]), self.format_subject_failure(session, reason), c)
        return self._client.client.mail.send.post(request_body=m.get())

    def check(self, options: dict):
        if not is_email(options["Email"]):
            raise KmVizQueryError(f"'{options['Email']}': not an email.")

    def options(self):
        return {"Email": update_option(TextOption("Email", "", "Your email"), {"is_required": True})}

