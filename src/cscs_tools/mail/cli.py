import argparse
from cscs_tools.mail.services.mail_service import MailService

def main():
    parser = argparse.ArgumentParser(description="Send email using cscs-tools MailService")

    parser.add_argument("--smtp-server", required=True, help="SMTP server hostname")
    parser.add_argument("--smtp-port", type=int, default=25, help="SMTP port (default: 25)")
    parser.add_argument("--security", choices=["NONE", "STARTTLS", "SSL"], default="STARTTLS",
                        help="Security mode (default: STARTTLS)")
    parser.add_argument("--user", help="SMTP username")
    parser.add_argument("--password", help="SMTP password")

    parser.add_argument("--from", dest="from_addr", required=True, help="From email address")
    parser.add_argument("--to", required=True, help="Recipient(s), comma separated")

    parser.add_argument("--subject", default="", help="Email subject")
    parser.add_argument("--body", default="", help="Plain text body")
    parser.add_argument("--html", help="Path to HTML file for HTML email")

    parser.add_argument("--attach", action="append", help="Attach files (can repeat)")

    args = parser.parse_args()

    from cscs_tools.mail.enums.security_mode import SecurityMode

    svc = MailService(
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        from_address=args.from_addr,
        smtp_username=args.user,
        smtp_password=args.password,
        security=SecurityMode[args.security],
    )

    if args.html:
        svc.send_html(args.to, args.html, subject=args.subject, attachments=args.attach)
    else:
        svc.send(args.to, args.body, subject=args.subject, attachments=args.attach)