from enum import Enum


class SecurityMode(Enum):
    STARTTLS = "starttls"
    SSL = "ssl"
    PLAIN = "plain"
