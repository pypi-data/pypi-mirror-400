from dataclasses import dataclass, field

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class Technique(BaseModel):
    """
    The Technique object describes the technique ID and/or name associated to an attack, as defined by ATT&CK MatrixTM.


    Attributes:
    - Name (name) [Recommended]: The name of the attack technique, as defined by ATT&CK MatrixTM.
    - Source URL (src_url) [Optional]: The versioned permalink of the attack technique, as defined by ATT&CK MatrixTM.
    - Unique ID (uid) [Recommended]: The unique identifier of the attack technique, as defined by ATT&CK MatrixTM.
    """

    name: str = None
    src_url: str = None
    uid: str = None


@dataclass
class Tactic(BaseModel):
    """
    The Tactic object describes the tactic ID and/or name that is associated to an attack, as defined by ATT&CK MatrixTM.


    Attributes:
    - Name (name) [Optional]: The tactic name that is associated with the attack technique, as defined by ATT&CK MatrixTM. For example: Reconnaissance.
    - Source URL (src_url) [Optional]: The versioned permalink of the attack tactic, as defined by ATT&CK MatrixTM. For example: https://attack.mitre.org/versions/v14/tactics/TA0043/.
    - Unique ID (uid) [Recommended]: The tactic ID that is associated with the attack technique, as defined by ATT&CK MatrixTM. For example: TA0043.
    """

    name: str = None
    src_url: str = None
    uid: str = None


@dataclass
class SubTechnique(BaseModel):
    """
    The Sub Technique object describes the sub technique ID and/or name associated to an attack, as defined by ATT&CK MatrixTM.


    Attributes:
    - Name (name) [Optional]: The name of the attack sub technique, as defined by ATT&CK MatrixTM. For example: Scanning IP Blocks.
    - Source URL (src_url) [Optional]: The versioned permalink of the attack sub technique, as defined by ATT&CK MatrixTM. For example: https://attack.mitre.org/versions/v14/techniques/T1595/001/.
    - Unique ID (uid) [Recommended]: The unique identifier of the attack sub technique, as defined by ATT&CK MatrixTM. For example: T1595.001.
    """

    name: str = None
    src_url: str = None
    uid: str = None


@dataclass
class MITREAttack(BaseModel):
    """
    The MITRE ATT&CK® object describes the tactic, technique & sub-technique associated to an attack as defined in ATT&CK MatrixTM.

    Attributes:
    - Sub Technique (sub_technique) [Optional]: The Sub Technique object describes the sub technique ID and/or name associated to an attack, as defined by ATT&CK MatrixTM.
    - Tactic (tactic) [Optional]: The Tactic object describes the tactic ID and/or name that is associated to an attack, as defined by ATT&CK MatrixTM.
    - Technique (technique) [Optional]: The Technique object describes the technique ID and/or name associated to an attack, as defined by ATT&CK MatrixTM.
    - Version (version) [Recommended]: The ATT&CK MatrixTM version.
    """

    sub_technique: SubTechnique = field(default_factory=SubTechnique)
    tactic: Tactic = field(default_factory=Tactic)
    technique: Technique = field(default_factory=Technique)
    version: str = None
