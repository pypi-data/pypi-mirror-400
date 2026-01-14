import json
from dataclasses import dataclass, field
from pprint import pprint

from py_mdr.ocsf_models.objects.actor import Actor
from py_mdr.ocsf_models.objects.api import API
from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.container import Container
from py_mdr.ocsf_models.objects.database import Database, Databucket
from py_mdr.ocsf_models.objects.device import Device
from py_mdr.ocsf_models.objects.dns_query import DNSQuery
from py_mdr.ocsf_models.objects.email import Email
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.network import NetworkEndpoint, NetworkConnectionInformation
from py_mdr.ocsf_models.objects.operating_system import Job
from py_mdr.ocsf_models.objects.process import Process
from py_mdr.ocsf_models.objects.url import UniformResourceLocator
from py_mdr.ocsf_models.objects.user import User


@dataclass
class EvidenceArtifacts(BaseModel):
    """
    A collection of evidence artifacts associated to the activity/activities that triggered a security detection.

    API Details (api) [recommended]: Describes details about the API call associated to the activity that triggered the detection.
    Actor (actor) [recommended]: Describes details about the user/role/process that was the source of the activity that triggered the detection.
    Connection Info (connection_info) [recommended]: Describes details about the network connection associated to the activity that triggered the detection.
    Container (container) [recommended]: Describes details about the container associated to the activity that triggered the detection.
    DNS Query (query) [recommended]: Describes details about the DNS query associated to the activity that triggered the detection.
    Data (data) [optional]: Additional evidence data that is not accounted for in the specific evidence attributes.
    Database (database) [recommended]: Describes details about the database associated to the activity that triggered the detection.
    Databucket (databucket) [recommended]: Describes details about the databucket associated to the activity that triggered the detection.
    Destination Endpoint (dst_endpoint) [recommended]: Describes details about the destination of the network activity that triggered the detection.
    Device (device) [recommended]: An addressable device, computer system or host associated to the activity that triggered the detection.
    Email (email) [recommended]: The email object associated to the activity that triggered the detection.
    File (file) [recommended]: Describes details about the file associated to the activity that triggered the detection.
    Job (job) [recommended]: Describes details about the scheduled job that was associated with the activity that triggered the detection.
    Process (process) [recommended]: Describes details about the process associated to the activity that triggered the detection.
    Registry Key win (reg_key) [recommended]: Describes details about the registry key that triggered the detection.
    Registry Value win (reg_value) [recommended]: Describes details about the registry value that triggered the detection.
    Source Endpoint (src_endpoint) [recommended]: Describes details about the source of the network activity that triggered the detection.
    URL (url) [recommended]: The URL object that pertains to the event or object associated to the activity that triggered the detection.
    User (user) [recommended]: Describes details about the user that was the target or somehow else associated with the activity that triggered the detection.
    Windows Service win (win_service) [recommended]: Describes details about the Windows service that triggered the detection.
    """

    api: API = field(default_factory=API)
    actor: Actor = field(default_factory=Actor)
    connection_info: NetworkConnectionInformation = field(default_factory=NetworkConnectionInformation)
    container: Container = field(default_factory=Container)
    query: DNSQuery = field(default_factory=DNSQuery)
    data: dict = field(default_factory=dict)
    database: Database = field(default_factory=Database)
    databucket: Databucket = field(default_factory=Databucket)
    dst_endpoint: NetworkEndpoint = field(default_factory=NetworkEndpoint)
    device: Device = field(default_factory=Device)
    email: Email = field(default_factory=Email)
    file: File = field(default_factory=File)
    job: Job = field(default_factory=Job)
    process: Process = field(default_factory=Process)
    # TODO: reg_key: RegistryKey = field(default_factory=RegistryKey)
    # TODO: reg_value: RegistryValue = field(default_factory=RegistryValue)
    src_endpoint: NetworkEndpoint = field(default_factory=NetworkEndpoint)
    url: UniformResourceLocator = field(default_factory=UniformResourceLocator)
    user: User = field(default_factory=User)
    # TODO: win_service: WindowsService = field(default_factory=WindowsService)

