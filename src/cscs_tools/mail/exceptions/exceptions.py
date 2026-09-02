class MailException(Exception):
    pass


class MailConnectionException(MailException):
    pass


class MailAuthenticationException(MailException):
    pass