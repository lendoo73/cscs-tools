from cscs_tools.mail.services.mail_service import MailService

# Required configuration
mail = MailService(
    smtp_server="smtp.mycompany.com",
    from_address="do-not.reply@mycompany.com"
)

# Basic text email
mail.send(
    to="myemail@gmail.com",
    text_body="Hello World."
)

# Email with optional subject and attachments
mail.send(
    to="myemail@gmail.com",
    subject="Test mail",
    text_body="Hello World.",
    attachments=["log/access.log", "log/error.log"]
)

# HTML email using an HTML file as the body
mail.send_html(
    to="myemail@gmail.com",
    subject="Test mail",  # optional
    html_file_path="sample/mail/test_email.html",
    attachments=["log/access.log", "log/error.log"] # optional
)
