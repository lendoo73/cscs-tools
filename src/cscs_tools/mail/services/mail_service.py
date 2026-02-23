import mimetypes
import smtplib
import ssl
from collections.abc import Iterable
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from cscs_tools.mail.enums.security_mode import SecurityMode


class MailService:
    def __init__(
        self,
        smtp_server: str,
        from_address: str,
        smtp_port: int=25,
        smtp_username: str=None,
        smtp_password: str=None,
        security:SecurityMode=SecurityMode.STARTTLS,
        timeout: int=15,
        charset: str="utf-8",
        debug: bool = False,
    ):
        self.from_address = from_address
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.security = security
        self.timeout = timeout
        self.charset = charset
        self.debug = debug

        if not isinstance(self.security, SecurityMode):
            raise ValueError("security must be a SecurityMode enum value")

    def send(self, to, text_body, subject=None, attachments: list[str]=None):
        rcpt = normalize_recipients(to)
        msg = MIMEMultipart()
        msg["From"] = self.from_address
        msg["To"] = ", ".join(rcpt)
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body, "plain", _charset=self.charset))

        if attachments:
            attach_files(msg, attachments)

        server = None
        try:
            server = self._create_server()
            server.sendmail(self.from_address, rcpt, msg.as_string())
        except Exception:
            raise
        finally:
            try:
                if server:
                    server.quit()
            except Exception:
                raise

    def send_html(self, to, subject: str, html_file_path: str, attachments: list[str]=None):
        with open(html_file_path, "r", encoding=self.charset) as f:
            html = f.read()

        rcpt = normalize_recipients(to)
        msg = MIMEMultipart("mixed")
        msg["From"] = self.from_address
        msg["To"] = ", ".join(rcpt)
        msg["Subject"] = subject

        if attachments:
            alt = MIMEMultipart("alternative")
            alt.attach(MIMEText(html, "html", _charset=self.charset))
            msg.attach(alt)

            attach_files(msg, attachments)

        else:
            msg.attach(MIMEText(html, "html", _charset=self.charset))

        server = None
        try:
            server = self._create_server()
            server.sendmail(self.from_address, rcpt, msg.as_string())
        finally:
            if server:
                server.quit()

    def _create_server(self):
        if self.security == SecurityMode.SSL:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(
                self.smtp_server,
                self.smtp_port,
                timeout=self.timeout,
                context=context,
            )
        else:
            server = smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
                timeout=self.timeout
            )

        if self.debug:
            server.set_debuglevel(1)

        server.ehlo()

        if self.security == SecurityMode.STARTTLS:
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()

        if self.smtp_username and self.smtp_password:
            server.login(self.smtp_username, self.smtp_password)

        return server


def normalize_recipients(to) -> list[str]:
    if isinstance(to, str):
        if "," in to:
            return [addr.strip() for addr in to.split(",") if addr.strip()]
        return [to.strip()]
    if isinstance(to, Iterable):
        return [str(x).strip() for x in to if str(x).strip()]
    raise TypeError("`to` must be a string email, a comma-separated string, or an iterable of strings")

def attach_files(msg, attachments: list[str] = None):
    for file_path in attachments or []:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        ctype, encoding = mimetypes.guess_type(path.name)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        with open(path, "rb") as f:
            if maintype == "text":
                # Use MIMEApplication for text to avoid unwanted re-encoding issues
                part = MIMEApplication(f.read(), _subtype=subtype)
            elif maintype == "image":
                part = MIMEImage(f.read(), _subtype=subtype)
            elif maintype == "audio":
                part = MIMEAudio(f.read(), _subtype=subtype)
            else:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())
                encoders.encode_base64(part)  # only needed when using MIMEBase

        part.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
        msg.attach(part)

