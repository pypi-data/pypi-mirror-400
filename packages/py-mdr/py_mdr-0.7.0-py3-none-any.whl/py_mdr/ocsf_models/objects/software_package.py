from dataclasses import dataclass, field
from enum import IntEnum

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.fingerprint import FingerPrint


class TypeID(IntEnum):
    """
    The type of software package.
    0	Unknown The type is unknown.
    1	Application An application software package.
    2	Operating System An operating system software package.
    99	Other The type is not mapped. See the type attribute, which contains a data source specific value.
    """
    Unknown = 0
    Application = 1
    OperatingSystem = 2
    Other = 99


@dataclass
class SoftwarePackage(BaseModel):
    """
    The Software Package object describes details about a software package. Defined by D3FEND d3f:SoftwarePackage.

    Architecture (architecture) [recommended]: Architecture is a shorthand name describing the type of computer hardware the packaged software is meant to run on.
    Epoch (epoch) [optional]: The software package epoch.
    Hash (hash) [optional]: Cryptographic hash to identify the binary instance of a software component.
    Name (name) [required]: The software package name.
    Package URL (purl) [optional]: A purl is a URL string used to identify and locate a software package in a mostly universal and uniform way across programming languages, package managers, packaging conventions, tools, APIs and databases.
    Software License (license) [optional]: The software license applied to this package.
    Software Release Details (release) [optional]: Release is the number of times a version of the software has been packaged.
    The product CPE identifier (cpe_name) [optional]: The Common Platform Enumeration (CPE) name as described by (NIST) For example: cpe:/a:apple:safari:16.
    Type (type) [optional]: The type of software package, normalized to the caption of the type_id value.
    Type ID (type_id) [recommended]: The type of software package.
    Vendor Name (vendor_name) [optional]: The name of the vendor who published the software package.
    Version (version) [required]: The software package version.
    """
    architecture: str = None
    epoch: int = None
    hash: FingerPrint = field(default_factory=FingerPrint)
    name: str = None
    purl: str = None
    license: str = None
    release: str = None
    cpe_name: str = None
    type: str = None
    type_id: TypeID = None
    vendor_name: str = None
    version: str = None
