from dataclasses import dataclass, field
from enum import IntEnum

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.fingerprint import FingerPrint
from py_mdr.ocsf_models.objects.remediation import Remediation
from py_mdr.ocsf_models.objects.user import User


@dataclass
class AffectedCode(BaseModel):
    """
    The Affected Code object describes details about a code block identified as vulnerable.

    End Line (end_line) [recommended]: The line number of the last line of code block identified as vulnerable.
    File O (file) [required]: Details about the file that contains the affected code block.
    Owner O (owner) [optional]: Details about the user that owns the affected file.
    Remediation Guidance (remediation) [optional]: Describes the recommended remediation steps to address identified issue(s).
    Start Line (start_line) [recommended]: The line number of the first line of code block identified as vulnerable.
    """
    end_line: int = None
    file: File = field(default_factory=File)
    owner: User = field(default_factory=User)
    remediation: Remediation = field(default_factory=Remediation)
    start_line: int = None


class TypeID(IntEnum):
    """
    The type of software package.
    """
    Unknown = 0
    Application = 1
    OperatingSystem = 2
    Other = 99


@dataclass
class AffectedSoftwarePackage(BaseModel):
    """
    The Affected Package object describes details about a software package identified as affected by a
    vulnerability/vulnerabilities.

    Architecture (architecture) [recommended]: Architecture is a shorthand name describing the type of computer hardware the packaged software is meant to run on.
    Epoch (epoch) [optional]: The software package epoch.
    Fixed In Version (fixed_in_version) [optional]: The software package version in which a reported vulnerability was patched/fixed.
    Hash O (hash) [optional]: Cryptographic hash to identify the binary instance of a software component.
    Name (name) [required]: The software package name.
    Package Manager (package_manager) [optional]: The software packager manager utilized to manage a package on a system, e.
    Package URL (purl) [optional]: A purl is a URL string used to identify and locate a software package in a mostly universal and uniform way across programming languages, package managers, packaging conventions, tools, APIs and databases.
    Path (path) [optional]: The installation path of the affected package.
    Remediation Guidance (remediation) [optional]: Describes the recommended remediation steps to address identified issue(s).
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
    fixed_in_version: str = None
    hash: FingerPrint = field(default_factory=FingerPrint)
    name: str = None
    package_manager: str = None
    purl: str = None
    path: str = None
    remediation: Remediation = field(default_factory=Remediation)
    license: str = None
    release: str = None
    cpe_name: str = None
    type: str = None
    type_id: TypeID = None
    vendor_name: str = None
    version: str = None
