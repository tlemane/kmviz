from .notifier import Notifier, NullNotifier
from kmviz.core.notifier.sendgrid import SendGridNotifier
from kmviz.core.notifier.smtp import SMTPNotifier

NOTIFIERS = {
    "sendgrid": SendGridNotifier,
    "smtp": SMTPNotifier
}

