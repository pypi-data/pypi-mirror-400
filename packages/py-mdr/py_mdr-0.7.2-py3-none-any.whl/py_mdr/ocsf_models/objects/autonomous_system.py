from dataclasses import dataclass

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class AutonomousSystem(BaseModel):
    """
    An autonomous system (AS) is a collection of connected Internet Protocol (IP) routing prefixes under the control
    of one or more network operators on behalf of a single administrative entity or domain that presents a common,
    clearly defined routing policy to the internet.

    Name (name) [recommended]: Organization name for the Autonomous System.
    Number (number) [recommended]: Unique number that the AS is identified by.
    """
    name: str = None
    number: int = None
