from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.user import User


class TypeID(IntEnum):
    Unknown: int = 0
    Other: int = 99
    Windows: int = 100
    Windows_Mobile: int = 101
    Linux: int = 200
    Android: int = 201
    MacOS: int = 300
    IOS: int = 301
    IPadOS: int = 302
    Solaris: int = 400
    AIX: int = 401
    HP_UX: int = 402


@dataclass
class OperatingSystem(BaseModel):
    """
    Represents the operating system, detailing its architecture, country, language, name, build, and specific editions or service packs.
    It encompasses both broad categorization and specific identifiers like CPE names.

    Attributes:
    - CPU Bits (cpu_bits) [Optional]: The cpu architecture, the number of bits used for addressing in memory. For example: 32 or 64.
    - Country (country) [Optional]: The operating system country code, as defined by the ISO 3166-1 standard (Alpha-2 code). For the complete list of country codes, see ISO 3166-1 alpha-2 codes.
    - Language (lang) [Optional]: The two letter lower case language codes, as defined by ISO 639-1. For example: en (English), de (German), or fr (French).
    - Name (name) [Optional]: The operating system name.
    - OS Build (build) [Optional]: The operating system build number.
    - OS Edition (edition) [Optional]: The operating system edition. For example: Professional.
    - OS Service Pack Name (sp_name) [Optional]: The name of the latest Service Pack.
    - OS Service Pack Version (sp_ver) [Optional]: The version number of the latest Service Pack.
    - The product CPE identifier (cpe_name) [Optional]: The Common Platform Enumeration (CPE) name as described by (NIST) For example: cpe:/a:apple:safari:16.2.
    - Type (type) [Optional]: The type of the operating system.
    - Type ID (type_id) [Optional]: The type identifier of the operating system.
    - Version (version) [Optional]: The version of the OS running on the device that originated the event. For example: "Windows 10", "OS X 10.7", or "iOS 9".
    """

    cpu_bits: int = None
    country: str = None
    lang: str = None
    name: str = None
    build: str = None
    edition: str = None
    sp_name: str = None
    sp_ver: int = None
    cpe_name: str = None
    type: str = None
    type_id: TypeID = None
    version: str = None


class RunStateID(IntEnum):
    """
    The run state ID of the job.
    """
    # The run state is unknown.
    Unknown = 0
    Ready = 1
    Queued = 2
    Running = 3
    Stopped = 4
    # The run state is not mapped. See the run_state attribute, which contains a data source specific value.
    Other = 99


@dataclass
class Job(BaseModel):
    """
    The Job object provides information about a scheduled job or task, including its name, command line, and state.
    It encompasses attributes that describe the properties and status of the scheduled job.

    Command Line O (cmd_line) [recommended]: The job command line.
    Created Time (created_time) [recommended]: The time when the job was created.
    Description (desc) [recommended]: The description of the job.
    File O (file) [required]: The file that pertains to the job.
    Last Run (last_run_time) [recommended]: The time when the job was last run.
    Name (name) [required]: The name of the job.
    Next Run (next_run_time) [optional]: The time when the job will next be run.
    Run State (run_state) [optional]: The run state of the job.
    Run State ID (run_state_id) [recommended]: The run state ID of the job.
    User O (user) [optional]: The user that created the job.
    """
    cmd_line: str = None
    created_time: datetime = None
    desc: str = None
    file: File = field(default_factory=File)
    last_run_time: datetime = None
    name: str = None
    next_run_time: datetime = None
    run_state: str = None
    run_state_id: RunStateID = None
    user: User = field(default_factory=User)
