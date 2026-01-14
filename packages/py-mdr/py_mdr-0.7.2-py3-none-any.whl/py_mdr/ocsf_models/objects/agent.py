from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.policy import Policy


class AgentTypeID(IntEnum):
    """
    The normalized representation of an agent or sensor. E.g., EDR, vulnerability management, APM, backup &
    recovery, etc.
    """
    # The type is unknown.
    Unknown = 0
    # Any EDR sensor or agent. Or any tool that provides similar threat detection, anti-malware, anti-ransomware, or similar capabilities. E.g., Crowdstrike Falcon, Microsoft Defender for Endpoint, Wazuh.
    EndpointDetectionAndResponse = 1
    # Any DLP sensor or agent. Or any tool that provides similar data classification, data loss detection, and/or data loss prevention capabilities. E.g., Forcepoint DLP, Microsoft Purview, Symantec DLP.
    DataLossPrevention = 2
    # Any agent or sensor that provides backups, archival, or recovery capabilities. E.g., Azure Backup, AWS Backint Agent.
    BackupAndRecovery = 3
    # Any agent or sensor that provides Application Performance Monitoring (APM), active tracing, profiling, or other observability use cases and optionally forwards the logs. E.g., New Relic Agent, Datadog Agent, Azure Monitor Agent.
    PerformanceMonitoringAndObservability = 4
    # Any agent or sensor that provides vulnerability management or scanning capabilities. E.g., Qualys VMDR, Microsoft Defender for Endpoint, Crowdstrike Spotlight, Amazon Inspector Agent.
    VulnerabilityManagement = 5
    # Any agent or sensor that forwards logs to a 3rd party storage system such as a data lake or SIEM. E.g., Splunk Universal Forwarder, Tenzir, FluentBit, Amazon CloudWatch Agent, Amazon Kinesis Agent.
    LogForwarding = 6
    # Any agent or sensor responsible for providing Mobile Device Management (MDM) or Mobile Enterprise Management (MEM) capabilities. E.g., JumpCloud Agent, Esper Agent, Jamf Pro binary.
    MobileDeviceManagement = 7
    # Any agent or sensor that provides configuration management of a device, such as scanning for software, license management, or applying configurations. E.g., AWS Systems Manager Agent, Flexera, ServiceNow MID Server.
    ConfigurationManagement = 8
    # Any agent or sensor that provides remote access capabilities to a device. E.g., BeyondTrust, Amazon Systems Manager Agent, Verkada Agent.
    RemoteAccess = 9
    # The type is not mapped. See the type attribute, which contains a data source specific value.
    Other = 99


@dataclass
class Agent(BaseModel):
    """
    An Agent (also known as a Sensor) is typically installed on an Operating System (OS) and serves as a specialized
    software component that can be designed to monitor, detect, collect, archive, or take action. These activities and
    possible actions are defined by the upstream system controlling the Agent and its intended purpose. For instance,
    an Agent can include Endpoint Detection & Response (EDR) agents, backup/disaster recovery sensors, Application
    Performance Monitoring or profiling sensors, and similar software.
    """
    uid: str = None
    name: str = None
    policies: List[Policy] = field(default_factory=list)
    type: str = None
    version: str = None
    uid_alt: str = None
    type_id: AgentTypeID = None
    vendor_name: str = None
