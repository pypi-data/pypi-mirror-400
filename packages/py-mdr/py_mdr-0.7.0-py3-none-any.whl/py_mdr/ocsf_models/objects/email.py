from dataclasses import field, dataclass
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class Email(BaseModel):
    """
    The Email object describes the email metadata such as sender, recipients, and direction. Defined by D3FEND d3f:Email.

    Cc O (cc) [optional]: The email header Cc values, as defined by RFC 5322.
    Delivered To O (delivered_to) [optional]: The Delivered-To email header field.
    Email UID (uid) [recommended]: The email unique identifier.
    From O (from) [required]: The email header From values, as defined by RFC 5322.
    Message UID (message_uid) [recommended]: The email header Message-Id value, as defined by RFC 5322.
    Raw Header (raw_header) [optional]: The email authentication header.
    Reply To O (reply_to) [recommended]: The email header Reply-To values, as defined by RFC 5322.
    SMTP From O (smtp_from) [recommended]: The value of the SMTP MAIL FROM command.
    SMTP To O (smtp_to) [recommended]: The value of the SMTP envelope RCPT TO command.
    Size (size) [recommended]: The size in bytes of the email, including attachments.
    Subject (subject) [recommended]: The email header Subject value, as defined by RFC 5322.
    To O (to) [required]: The email header To values, as defined by RFC 5322.
    X-Originating-IP O (x_originating_ip) [optional]: The X-Originating-IP header identifying the emails originating IP address(es).
    """
    cc: List[str] = field(default_factory=list)
    delivered_to: str = None
    uid: str = None
    _from: str = None
    message_uid: str = None
    raw_header: str = None
    reply_to: str = None
    smtp_from: str = None
    smtp_to: List[str] = field(default_factory=list)
    size: int = None
    subject: str = None
    to: List[str] = field(default_factory=list)
    x_originating_ip: List[str] = field(default_factory=list)
