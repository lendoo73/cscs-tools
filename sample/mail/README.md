
# 📧 Mail Module (cscs_tools.mail)

Simple, dependency‑free helpers to send **text** and **HTML** emails with optional **attachments** over SMTP.

---

## ✅ Quick Start

```python
from cscs_tools.mail.services.mail_service import MailService

mail = MailService(
    smtp_server="smtp.mycompany.com",
    from_address="do-not.reply@mycompany.com",
)

mail.send(
    to="user1@example.com",
    text_body="Hello World.",
)
```

---

## ⚙️ MailService

### Required
- `smtp_server` – e.g. `smtp.mycompany.com`
- `from_address` – the visible From: address

### Optional (defaults)
- `smtp_port=25` – `25/587` for STARTTLS, `465` for SSL
- `smtp_username=None`, `smtp_password=None` – set if SMTP requires auth
- `security=SecurityMode.STARTTLS` – `STARTTLS | SSL | PLAIN`
- `timeout=15` – seconds
- `charset="utf-8"`
- `debug=False` – SMTP protocol debug output

---

## ✉️ Sending

### Text email
```python
mail.send(
    to="user@example.com",
    subject="Optional",
    text_body="Hi there!",
)
```

### With attachments
```python
mail.send(
    to=["a@example.com", "b@example.com"],
    subject="Attachments",
    text_body="Please see files.",
    attachments=["docs/info.txt", "images/pic.png"],
)
```

### HTML email
```python
mail.send_html(
    to="user@example.com",
    subject="HTML",
    html_file_path="sample/mail/test_email.html",
)
```

### HTML + attachments
```python
mail.send_html(
    to="user1@example.com, user2@example.com",
    subject="Report",
    html_file_path="sample/mail/test_email.html",
    attachments=["files/report.pdf"],
)
```

> **Recipients input**: You can pass a single email string, a comma‑separated string, or a list of strings. The library normalizes these and sends to all.

---

## 🔐 Security Modes

```python
from cscs_tools.mail.enums.security_mode import SecurityMode
```
- `SecurityMode.STARTTLS` – connect, then upgrade to TLS (recommended)
- `SecurityMode.SSL` – SMTPS (typically port 465)
- `SecurityMode.PLAIN` – no encryption (avoid unless strictly required)

---

## 📎 Attachments
- Provide file paths: `attachments=["path/to/file1", "path/to/file2"]`
- Any file type supported; common types are detected (images, pdf, text). Others are sent as `application/octet-stream`.
- Nonexistent paths raise `FileNotFoundError`.

---

## 📝 Notes
- The working directory affects relative paths like `sample/mail/test_email.html`.
- For multiple recipients, headers show a comma‑separated list; SMTP is called with the expanded list.
- For HTML with attachments, the message uses `multipart/mixed` with an inner `multipart/alternative` body.

---

## 🧪 Samples
See more examples in the repository’s `/sample` folder.

---

## 📄 License
MIT © Csaba Cselko
