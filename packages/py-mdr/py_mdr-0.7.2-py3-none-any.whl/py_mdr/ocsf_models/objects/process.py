from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List, Self

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.user import User


@dataclass
class IdentityProvider(BaseModel):
    """
    The Identity Provider object contains detailed information about a provider responsible for creating, maintaining,
    and managing identity information while offering authentication services to applications. An Identity Provider
    (IdP) serves as a trusted authority that verifies the identity of users and issues authentication tokens or
    assertions to enable secure access to applications or services.

    Name (name) [recommended]: The name of the identity provider.
    Unique ID (uid) [recommended]: The unique identifier of the identity provider.
    """
    name: str = None
    uid: str = None


@dataclass
class Session(BaseModel):
    """
    The Session object describes details about an authenticated session. e.g. Session Creation Time, Session Issuer.
    Defined by D3FEND d3f:Session.

    Alternate ID (uid_alt) [optional]: The alternate unique identifier of the session.
    Count (count) [optional]: The number of identical sessions spawned from the same source IP, destination IP, application, and content/threat type seen over a period of time.
    Created Time (created_time) [recommended]: The time when the session was created.
    Expiration Reason (expiration_reason) [optional]: The reason which triggered the session expiration.
    Expiration Time (expiration_time) [optional]: The session expiration time.
    Issuer Details (issuer) [recommended]: The identifier of the session issuer.
    Multi-Factor Authentication (is_mfa) [optional]: Indicates whether Multi-Factor Authentication was used during authentication.
    Remote (is_remote) [recommended]: The indication of whether the session is remote.
    Terminal (terminal) [optional]: The Pseudo Terminal associated with the session.
    UUID (uuid) [optional]: The universally unique identifier of the session.
    Unique ID (uid) [recommended]: The unique identifier of the session.
    User Credential ID O (credential_uid) [optional]: The unique identifier of the user's credential.
    VPN Session (is_vpn) [optional]: The indication of whether the session is a VPN session.
    """
    uid_alt: str = None
    count: int = None
    created_time: datetime = None
    expiration_reason: str = None
    expiration_time: datetime = None
    issuer: str = None
    is_mfa: bool = None
    is_remote: bool = None
    terminal: str = None
    uuid: str = None
    uid: str = None
    credential_uid: str = None
    is_vpn: bool = None


class IntegrityID(IntEnum):
    """
    The normalized identifier of the process integrity level (Windows only).
    0	Unknown The integrity level is unknown.
    1	Untrusted
    2	Low
    3	Medium
    4	High
    5	System
    6	Protected
    99	Other
    The integrity level is not mapped. See the integrity attribute, which contains a data source specific value.
    """
    Unknown = 0
    Untrusted = 1
    Low = 2
    Medium = 3
    High = 4
    System = 5
    Protected = 6
    Other = 99


@dataclass
class Process(BaseModel):
    """
    The Process object describes a running instance of a launched program.
    Defined by D3FEND d3f:Process.

    Command Line O (cmd_line) [recommended]: The full command line used to launch an application, service, process, or job.
    Created Time (created_time) [recommended]: The time when the process was created/started.
    Extended Attributes (xattributes) [optional]: An unordered collection of zero or more name/value pairs that represent a process extended attribute.
    File O (file) [recommended]: The process file object.
    Integrity (integrity) [optional]: The process integrity level, normalized to the caption of the integrity_id value.
    Integrity Level (integrity_id) [optional]: The normalized identifier of the process integrity level (Windows only).
    Lineage (lineage) [optional]: The lineage of the process, represented by a list of paths for each ancestor process.
    Loaded Modules (loaded_modules) [optional]: The list of loaded module names.
    Name O (name) [recommended]: The friendly name of the process, for example: Notepad++.
    Parent Process O (parent_process) [recommended]: The parent process of this process object.
    Process ID O (pid) [recommended]: The process identifier, as reported by the operating system.
    Sandbox (sandbox) [optional]: The name of the containment jail.
    Session (session) [optional]: The user session under which this process is running.
    Terminated Time (terminated_time) [optional]: The time when the process was terminated.
    Thread ID (tid) [optional]: The Identifier of the thread associated with the event, as returned by the operating system.
    Unique ID (uid) [recommended]: A unique identifier for this process assigned by the producer (tool).
    User O (user) [recommended]: The user under which this process is running.
    """
    cmd_line: str = None
    created_time: datetime = None
    xattributes: object = None
    file: File = field(default_factory=File)
    integrity: str = None
    integrity_id: IntegrityID = None
    lineage: List[str] = field(default_factory=list)
    loaded_modules: List[str] = field(default_factory=list)
    name: str = None
    parent_process: Self = None
    pid: int = None
    sandbox: str = None
    session: Session = field(default_factory=Session)
    terminated_time: datetime = None
    tid: int = None
    uid: str = None
    user: User = field(default_factory=User)
