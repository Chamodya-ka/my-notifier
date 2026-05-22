import json
import smtplib
import ssl
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EmailAuthentication, EmailConfig
from notifications.email_template_gen import EmailTemplateGen


class EmailClient:
    def __init__(self, config: EmailConfig):
        self.config = config
        self.email_template_gen = EmailTemplateGen()  # TODO: make this pluggable

    # ------------------------------------------------------------------ #
    #  Template                                                            #
    # ------------------------------------------------------------------ #

    def _build_payload(self, rule: str, line: str) -> dict:
        text_body = self.email_template_gen.fill(rule, line)
        return {
            "From": self.config.from_address,
            "To": self.config.to,
            "Subject": self.config.subject,
            "TextBody": text_body,
            "HtmlBody": f"<html><body>{text_body}</body></html>",
            "MessageStream": self.config.message_stream,
        }

    # ------------------------------------------------------------------ #
    #  Send via Postmark HTTP API (token auth)                            #
    # ------------------------------------------------------------------ #

    def _send_postmark(self, payload: dict):
        auth: EmailAuthentication = self.config.authentication
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.config.api_url,
            data=body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                auth.token_name: auth.token,
            },
        )
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))

    # ------------------------------------------------------------------ #
    #  Send via SMTP                                                       #
    # ------------------------------------------------------------------ #

    def _resolve_smtp_host_port(self) -> tuple[str, int]:
        if self.config.smtp_url:
            parsed = urllib.parse.urlparse(self.config.smtp_url)
            host = parsed.hostname or parsed.path
            port = parsed.port or self.config.smtp_port or 587
            return host, port
        return self.config.smtp_server, self.config.smtp_port or 587

    def _send_smtp(self, payload: dict):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = payload["Subject"]
        msg["From"] = payload["From"]
        msg["To"] = payload["To"]
        msg.attach(MIMEText(payload["TextBody"], "plain"))
        msg.attach(MIMEText(payload["HtmlBody"], "html"))

        host, port = self._resolve_smtp_host_port()
        context = ssl.create_default_context()

        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(self.config.username, self.config.password)
            server.sendmail(payload["From"], payload["To"], msg.as_string())

    # ------------------------------------------------------------------ #
    #  Public                                                              #
    # ------------------------------------------------------------------ #

    def send(self, rule: str, line: str):
        payload = self._build_payload(rule, line)

        if self.config.authentication:
            res = self._send_postmark(payload)
            # print(res)
        elif self.config.username and self.config.password:
            res = self._send_smtp(payload)
        else:
            raise ValueError(
                "EmailConfig requires either a 'token' (Postmark) "
                "or 'username' + 'password' (SMTP)."
            )
