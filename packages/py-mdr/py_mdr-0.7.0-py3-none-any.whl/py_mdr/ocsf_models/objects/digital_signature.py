from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.digital_certificate import DigitalCertificate
from py_mdr.ocsf_models.objects.fingerprint import AlgorithmID, FingerPrint


class StateID(IntEnum):
    """
    The Digital Signature object contains information about the cryptographic mechanism used to verify the authenticity,
     integrity, and origin of the file or application.
    """
    Unknown = 0
    Valid = 1
    Expired = 2
    Revoked = 3
    Suspended = 4
    Pending = 5
    Other = 99


@dataclass
class DigitalSignature(BaseModel):
    """
    The Digital Signature object contains information about the cryptographic mechanism used to verify the authenticity,
    integrity, and origin of the file or application.

    Algorithm (algorithm) [optional]: The digital signature algorithm used to create the signature, normalized to the caption of 'algorithm_id'.
    Algorithm ID (algorithm_id) [required]: The identifier of the normalized digital signature algorithm.
    Certificate (certificate) [recommended]: The certificate object containing information about the digital certificate.
    Created Time (created_time) [optional]: The time when the digital signature was created.
    Developer UID (developer_uid) [optional]: The developer ID on the certificate that signed the file.
    Message Digest O (digest) [optional]: The message digest attribute contains the fixed length message hash representation and the corresponding hashing algorithm information.
    State (state) [optional]: The digital signature state defines the signature state, normalized to the caption of 'state_id'.
    State ID (state_id) [optional]: The normalized identifier of the signature state.
    """
    algorithm: str = None
    algorithm_id: AlgorithmID = None
    certificate: DigitalCertificate = field(default_factory=DigitalCertificate)
    created_time: datetime = None
    developer_uid: str = None
    digest: FingerPrint = field(default_factory=FingerPrint)
    state: str = None
    state_id: StateID = None
