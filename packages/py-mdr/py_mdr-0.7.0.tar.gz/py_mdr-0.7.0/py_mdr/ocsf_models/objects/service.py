from dataclasses import dataclass, field

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class Service(BaseModel):
    """
    Encapsulates information about a service, including its name, unique identifier, version, and any associated labels.
    This model is designed to represent services in a microservices architecture or within any application ecosystem, providing
    a way to uniquely identify and describe services.

    Attributes:
    - Labels (labels) [Optional]: A list of labels or tags associated with the service, providing additional metadata.
    - Name (name) [Optional]: The name of the service, clearly identifying it within the system.
    - Unique ID	 (uid) [Optional]: A unique identifier for the service, ensuring distinct recognition.
    - Version (version) [Optional]: The version of the service, helping to track changes or updates over time.
    """

    labels: list[str] = field(default_factory=list)
    name: str = None
    uid: str = None
    version: str = None
