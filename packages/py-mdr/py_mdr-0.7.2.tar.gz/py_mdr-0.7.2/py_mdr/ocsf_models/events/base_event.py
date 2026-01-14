from dataclasses import dataclass

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class BaseEvent(BaseModel):
    """
    Dummy class for all events to derive from. This is for checking that
    all Events have a Metadata class attached.
    """
    pass
