from dataclasses import dataclass, field
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.kill_chain_phase import KillChainPhase
from py_mdr.ocsf_models.objects.mitre_attack import MITREAttack
from py_mdr.ocsf_models.objects.observable import Observable


@dataclass
class RelatedEvent(BaseModel):
    """
    Model representing a related event.

    The RelatedEvent class encapsulates information about an event related to a security incident,
    including details such as the Cyber Kill Chain phase, MITRE ATT&CK® details, observables,
    product identifier, event type, event type identifier, and unique identifier.

    Attributes:
    - Kill Chain (kill_chain) [Optional]: The Cyber Kill Chain® provides a detailed description of each phase and its associated activities within the broader context of a cyberattack.
    - MITRE ATT&CK® Details (attacks) [Optional]: An array of MITRE ATT&CK® objects describing the tactics, techniques & sub-techniques identified by a security control or finding.
    - Observables (observables) [Optional]: The observables associated with the event or a finding.
    - Product Identifier (product_uid) [Optional]: The unique identifier of the product that reported the related event.
    - Type (type) [Optional]: The type of the related event. For example: Process Activity: Launch.
    - Type ID (type_uid) [Recommended]: The unique identifier of the related event type. For example: 100701.
    - Unique ID (uid) [Required]: The unique identifier of the related event.
    """

    kill_chain: List[KillChainPhase] = field(default_factory=list)
    attacks: List[MITREAttack] = field(default_factory=list)
    observables: List[Observable] = field(default_factory=list)
    product_uid: str = None
    type: str = None
    type_uid: int = None
    uid: str = None
