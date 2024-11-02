# Notifier

## SendGrid

<div class="grid" markdown>

```toml title="sendgrid_ex.toml"
[notif]
type = "sendgrid"
success = """
Dear user,

Your query over is complete.

Please visit http://localhost:8050/api/download/{SESSION}' to download your results. You can also visit 'http://localhost:8050/dashboard/{SESSION}' to visualize them using our web interface.
"""

failure = """
Dear user,

Your query over failed. (session: {SESSION})
Reason: {REASON}
"""

subject = """
[kmviz] {SESSION} ✅
"""

subject_failure = """
[kmviz] {SESSION} ❌

[notif.params]
api_key = "<sendgrid api key>"
sender = "sender@sender.com"
```
</div>

## SMTP

<div class="grid" markdown>

```toml title="smtp_ex.toml"
[notif]
type = "smtp"
success = """
Dear user,

Your query over is complete.

Please visit http://localhost:8050/api/download/{SESSION}' to download your results. You can also visit 'http://localhost:8050/dashboard/{SESSION}' to visualize them using our web interface.
"""

failure = """
Dear user,

Your query over failed. (session: {SESSION})
Reason: {REASON}
"""

subject = """
[kmviz] {SESSION} ✅
"""

subject_failure = """
[kmviz] {SESSION} ❌

[notif.params]
sender = "sender@sender.com"
server = "mysmtp.server.com"
user = "user"
password = "password"
```

</div>
