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
    """
    A service for sending plain-text and HTML emails with optional attachments.

    This class wraps SMTP/SMTP-SSL connections with optional STARTTLS,
    authentication, and a configurable timeout/charset. It supports sending
    simple text emails or HTML emails (with mixed/alternative parts when
    attachments are included).

    Attributes
    ----------
    from_address : str
        Sender email address used in the "From" header.
    smtp_server : str
        Hostname or IP address of the SMTP server.
    smtp_port : int
        Port number for SMTP/SMTP-SSL connections.
    smtp_username : str or None
        Username for SMTP authentication (if required).
    smtp_password : str or None
        Password for SMTP authentication (if required).
    security : SecurityMode
        Security mode for the connection (NONE, STARTTLS, or SSL).
    timeout : int
        Socket timeout in seconds for SMTP operations.
    charset : str
        Default character set used for message bodies.
    debug : bool
        Enables SMTP debug output when True.

    Parameters
    ----------
    smtp_server : str
        SMTP server hostname or IP.
    from_address : str
        Sender email address.
    smtp_port : int, optional
        SMTP port (default is 25).
    smtp_username : str, optional
        SMTP username if authentication is required (default is None).
    smtp_password : str, optional
        SMTP password if authentication is required (default is None).
    security : SecurityMode, optional
        Connection security (default is SecurityMode.STARTTLS).
    timeout : int, optional
        SMTP socket timeout in seconds (default is 15).
    charset : str, optional
        Default charset for message bodies (default is "utf-8").
    debug : bool, optional
        Enable SMTP library debug output (default is False).

    Methods
    -------
    send(to, text_body, subject=None, attachments=None)
        Send a plain-text email with optional attachments.
    send_html(to, html_file_path, subject=None, attachments=None)
        Send an HTML email (file-based body) with optional attachments.

    Examples
    --------
    >>> svc = MailService(
    ...     smtp_server="smtp.example.com",
    ...     from_address="noreply@example.com",
    ...     smtp_port=587,
    ...     smtp_username="user",
    ...     smtp_password="pass",
    ...     security=SecurityMode.STARTTLS
    ... )
    >>> svc.send("alice@example.com", "Hello!", subject="Greetings")
    >>> svc.send_html(
    ...     ["a@example.com", "b@example.com"],
    ...     "templates/report.html",
    ...     subject="Weekly Report",
    ...     attachments=["/path/to/report.pdf"]
    ... )
    """
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

        """
        Initialize the MailService with SMTP connection and message defaults.

        Parameters
        ----------
        smtp_server : str
            SMTP server hostname or IP.
        from_address : str
            Sender email address.
        smtp_port : int, optional
            SMTP port (default is 25).
        smtp_username : str or None, optional
            Username for SMTP auth (default is None).
        smtp_password : str or None, optional
            Password for SMTP auth (default is None).
        security : SecurityMode, optional
            Security mode (NONE, STARTTLS, SSL). Default is STARTTLS.
        timeout : int, optional
            Socket timeout in seconds (default is 15).
        charset : str, optional
            Default charset for message bodies (default is "utf-8").
        debug : bool, optional
            Enable SMTP debug logs when True (default is False).

        Raises
        ------
        ValueError
            If `security` is not a SecurityMode enum value.
        """
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
        """
        Send a plain-text email to one or more recipients.

        Parameters
        ----------
        to : str or Iterable[str]
            Recipient(s) as a single email, comma-separated string, or iterable.
        text_body : str
            Plain-text message body.
        subject : str, optional
            Email subject (default is None).
        attachments : list[str], optional
            File paths to attach (default is None).

        Raises
        ------
        FileNotFoundError
            If a specified attachment does not exist.
        TypeError
            If `to` is not a string or iterable of strings.
        smtplib.SMTPException
            For SMTP-related errors (connection, authentication, send).
        """
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

    def send_html(self, to, html_file_path: str, subject=None, attachments: list[str]=None):
        """
        Send an HTML email using the contents of a local file.

        If attachments are provided, the message is structured as
        multipart/mixed with an alternative (HTML) part.

        Parameters
        ----------
        to : str or Iterable[str]
            Recipient(s) as a single email, comma-separated string, or iterable.
        html_file_path : str
            Path to the HTML file used as the message body.
        subject : str, optional
            Email subject (default is None).
        attachments : list[str], optional
            File paths to attach (default is None).

        Raises
        ------
        FileNotFoundError
            If `html_file_path` does not exist.
        TypeError
            If `to` is not a string or iterable of strings.
        smtplib.SMTPException
            For SMTP-related errors (connection, authentication, send).
        """
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
        """
        Create and configure an SMTP or SMTP_SSL client.

        Applies STARTTLS when requested, sets debug level, performs
        EHLO/HELO, and logs in if credentials are provided.

        Returns
        -------
        smtplib.SMTP
            Configured SMTP-like client (SMTP or SMTP_SSL).

        Raises
        ------
        smtplib.SMTPException
            For connection, TLS negotiation, or authentication errors.
        """

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
    """
    Normalize recipient input into a clean list of email addresses.

    Accepts a single email string, a comma-separated string, or any iterable
    of strings. Whitespace is stripped and empty entries are removed.

    Parameters
    ----------
    to : str or Iterable[str]
        Recipient input as a string (single or comma-separated) or iterable.

    Returns
    -------
    list[str]
        List of non-empty, stripped email addresses.

    Raises
    ------
    TypeError
        If `to` is not a string or an iterable of strings.

    Examples
    --------
    >>> normalize_recipients("a@example.com, b@example.com")
    ['a@example.com', 'b@example.com']
    >>> normalize_recipients(["a@example.com", "  "])
    ['a@example.com']
    """
    if isinstance(to, str):
        if "," in to:
            return [addr.strip() for addr in to.split(",") if addr.strip()]
        return [to.strip()]
    if isinstance(to, Iterable):
        return [str(x).strip() for x in to if str(x).strip()]
    raise TypeError("`to` must be a string email, a comma-separated string, or an iterable of strings")

def attach_files(msg, attachments: list[str] = None):
    """
    Attach files to a multipart email message using appropriate MIME types.

    Guesses content types, creates a matching MIME part (image, audio, text,
    or generic application/octet-stream), applies base64 encoding when needed,
    and adds a Content-Disposition header with the original filename.

    Parameters
    ----------
    msg : email.mime.multipart.MIMEMultipart
        The multipart message to which attachments will be added.
    attachments : list[str], optional
        Paths of files to attach (default is None).

    Raises
    ------
    FileNotFoundError
        If any attachment path does not exist.

    Notes
    -----
    - Text files are attached using MIMEApplication to avoid re-encoding issues.
    - Fallback type is application/octet-stream when type cannot be determined.

    Examples
    --------
    >>> msg = MIMEMultipart()
    >>> attach_files(msg, ["report.pdf", "image.png"])
    """
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
                part = MIMEApplication(f.read(), _subtype=subtype)
            elif maintype == "image":
                part = MIMEImage(f.read(), _subtype=subtype)
            elif maintype == "audio":
                part = MIMEAudio(f.read(), _subtype=subtype)
            else:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())
                encoders.encode_base64(part)

        part.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
        msg.attach(part)