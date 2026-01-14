from dataclasses import dataclass

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class Organization(BaseModel):
    """
    The Organization object describes characteristics of an organization or company and its division if any.

    Attributes:
    - Name (name): The name of the organization. For example, Widget, Inc.
    - Org Unit ID (ou_uid) [Optional]: The alternate identifier for an entity's unique identifier. For example, its Active Directory OU DN or AWS OU ID
    - Org Unit Name	(ou_name): The name of the organizational unit, within an organization. For example, Finance, IT, R&D
    - Unique ID	(uid): The unique identifier of the organization. For example, its Active Directory or AWS Org ID.
    """

    name: str = None
    ou_uid: str = None
    ou_name: str = None
    uid: str = None
