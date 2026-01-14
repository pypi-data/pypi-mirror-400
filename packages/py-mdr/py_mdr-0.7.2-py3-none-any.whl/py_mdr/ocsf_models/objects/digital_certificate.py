from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.fingerprint import FingerPrint


@dataclass
class DigitalCertificate(BaseModel):
    """
    The Digital Certificate, also known as a Public Key Certificate, object contains information about the ownership
    and usage of a public key. It serves as a means to establish trust in the authenticity and integrity of the public
    key and the associated entity. Defined by D3FEND d3f:Certificate.

    Certificate Self-Signed (is_self_signed) [recommended]: Denotes whether a digital certificate is self-signed or signed by a known certificate authority (CA).
    Certificate Serial Number (serial_number) [required]: The serial number of the certificate used to create the digital signature.
    Created Time (created_time) [recommended]: The time when the certificate was created.
    Expiration Time (expiration_time) [recommended]: The expiration time of the certificate.
    Fingerprints O (fingerprints) [required]: The fingerprint list of the certificate.
    Issuer Distinguished Name (issuer) [required]: The certificate issuer distinguished name.
    Subject Distinguished Name (subject) [recommended]: The certificate subject distinguished name.
    Unique ID (uid) [optional]: The unique identifier of the certificate.
    Version (version) [recommended]: The certificate version.
    """
    is_self_signed: bool = None
    serial_number: str = None
    created_time: datetime = None
    expiration_time: datetime = None
    fingerprints: List[FingerPrint] = field(default_factory=FingerPrint)
    issuer: str = None
    subject: str = None
    uid: str = None
    version: str = None
