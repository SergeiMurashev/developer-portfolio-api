import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import Settings


@dataclass
class SMTPResult:
    sent: bool
    error: str | None = None


class SMTPClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, *, to_email: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.settings.smtp_from
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=self.settings.smtp_timeout_seconds) as client:
            if self.settings.smtp_use_tls:
                client.starttls()
            if self.settings.smtp_username:
                client.login(self.settings.smtp_username, self.settings.smtp_password)
            client.send_message(message)

