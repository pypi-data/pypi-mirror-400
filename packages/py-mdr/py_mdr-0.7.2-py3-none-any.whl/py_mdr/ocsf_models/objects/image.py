from dataclasses import dataclass

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class Image(BaseModel):
    """
    Represents a container image, detailing its name, optional tag, labels, and unique identifier.
    The class encapsulates the core attributes that define a container image in a containerized environment.

    Attributes:
    - tag (str): The image tag, specifying version or variant, e.g., '1.11-alpine'.
    - labels (list[str]): Metadata labels associated with the image.
    - name (str): The name of the image, e.g., 'elixir'.
    - path (str): The full path to the image file on the host or in the repository.
    - uid (str): A unique identifier for the image, e.g., '77af4d6b9913'.
    """

    tag: str = None
    labels: list[str] = None
    name: str = None
    path: str = None
    uid: str = None
