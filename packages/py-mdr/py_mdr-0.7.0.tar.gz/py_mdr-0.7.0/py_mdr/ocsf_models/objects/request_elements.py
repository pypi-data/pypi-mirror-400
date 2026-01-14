from dataclasses import dataclass, field

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.container import Container


@dataclass
class RequestElements(BaseModel):
    """
    Represents the elements of an API request, especially in containerized applications.
    It includes details about the containers involved, any additional data associated with the request,
    communication flags, and a unique identifier for the request.

    Attributes:
    - containers: An array of containers involved in the API request/response process.
    - data: Additional JSON-formatted data associated with the API request.
    - flags: A list of communication flags indicating specific characteristics or behaviors of the request.
    - uid: A unique identifier for the API request.
    """

    containers: list[Container] = field(default_factory=list)
    data: dict[str, object] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)
    uid: str = None
