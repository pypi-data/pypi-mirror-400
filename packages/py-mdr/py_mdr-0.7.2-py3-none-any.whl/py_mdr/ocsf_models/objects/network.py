import ipaddress
from dataclasses import field, dataclass
from enum import IntEnum
from typing import List

from py_mdr.ocsf_models.objects.agent import Agent
from py_mdr.ocsf_models.objects.autonomous_system import AutonomousSystem
from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.device_hardware_info import DeviceHardwareInfo
from py_mdr.ocsf_models.objects.geolocation import GeoLocation
from py_mdr.ocsf_models.objects.operating_system import OperatingSystem
from py_mdr.ocsf_models.objects.process import Session
from py_mdr.ocsf_models.objects.user import User


class NetworkTypeID(IntEnum):
    """
    The network endpoint type ID.
    """
    # The type is unknown.
    Unknown = 0
    # A server.
    Server = 1
    # A desktop computer.
    Desktop = 2
    # A laptop computer.
    Laptop = 3
    # A tablet computer.
    Tablet = 4
    # A mobile phone.
    Mobile = 5
    # A virtual machine.
    Virtual = 6
    # An IOT (Internet of Things) device.
    IOT = 7
    # A web browser.
    Browser = 8
    # A networking firewall.
    Firewall = 9
    # A networking switch.
    Switch = 10
    # A networking hub.
    Hub = 11
    # A networking router.
    Router = 12
    # An intrusion detection system.
    IDS = 13
    # An intrusion prevention system.
    IPS = 14
    # A Load Balancer device.
    LoadBalancer = 15
    # The type is not mapped. See the type attribute, which contains a data source specific value.
    Other = 99


@dataclass
class NetworkProxyEndpoint(BaseModel):
    """
    The network proxy endpoint object describes a proxy server, which acts as an intermediary between a client
    requesting a resource and the server providing that resource. Defined by D3FEND d3f:ProxyServer.

    Agent List (agent_list) [optional]: A list of agent objects associated with a device, endpoint, or resource.
    Autonomous System (autonomous_system) [optional]: The Autonomous System details associated with an IP address.
    Domain (domain) [optional]: The name of the domain.
    Geo Location O (location) [optional]: The geographical location of the endpoint.
    Hardware Info (hw_info) [optional]: The endpoint hardware information.
    Hostname O (hostname) [recommended]: The fully qualified name of the endpoint.
    IP Address O (ip) [recommended]: The IP address of the endpoint, in either IPv4 or IPv6 format.
    Instance ID (instance_uid) [recommended]: The unique identifier of a VM instance.
    Intermediate IP Addresses O (intermediate_ips) [optional]: The intermediate IP Addresses.
    MAC Address O (mac) [optional]: The Media Access Control (MAC) address of the endpoint.
    Name (name) [recommended]: The short name of the endpoint.
    Network Interface ID (interface_uid) [recommended]: The unique identifier of the network interface.
    Network Interface Name (interface_name) [recommended]: The name of the network interface.
    Network Zone (zone) [optional]: The network zone or LAN segment.
    OS (os) [optional]: The endpoint operating system.
    Owner O (owner) [recommended]: The identity of the service or user account that owns the endpoint or was last logged into it.
    Port O (port) [recommended]: The port used for communication within the network connection.
    Proxy Endpoint O (proxy_endpoint) [optional]: The network proxy information pertaining to a specific endpoint.
    Service Name (svc_name) [recommended]: The service name in service-to-service connections.
    Subnet UID (subnet_uid) [optional]: The unique identifier of a virtual subnet.
    Type (type) [optional]: The network endpoint type.
    Type ID (type_id) [recommended]: The network endpoint type ID.
    Unique ID (uid) [recommended]: The unique identifier of the endpoint.
    VLAN (vlan_uid) [optional]: The Virtual LAN identifier.
    VPC UID (vpc_uid) [optional]: The unique identifier of the Virtual Private Cloud (VPC).
    """
    agent_list: List[Agent] = field(default_factory=Agent)
    autonomous_system: AutonomousSystem = field(default_factory=AutonomousSystem)
    domain: str = None
    location: GeoLocation = field(default_factory=GeoLocation)
    hw_info: DeviceHardwareInfo = field(default_factory=DeviceHardwareInfo)
    hostname: str = None
    ip: ipaddress.ip_address = None
    instance_uid: str = None
    intermediate_ips: List[ipaddress.ip_address] = field(default_factory=list)
    mac: str = None
    name: str = None
    interface_uid: str = None
    interface_name: str = None
    zone: str = None
    os: OperatingSystem = field(default_factory=OperatingSystem)
    owner: User = field(default_factory=User)
    port: int = None
    proxy_endpoint: "NetworkProxyEndpoint" = None
    svc_name: str = None
    subnet_uid: str = None
    type: str = None
    type_id: NetworkTypeID = None
    uid: str = None
    vlan_uid: str = None
    vpc_uid: str = None


@dataclass
class NetworkEndpoint(BaseModel):
    """
    The Network Endpoint object describes characteristics of a network endpoint. These can be a source or destination
    of a network connection.

    Agent List (agent_list) [optional]: A list of agent objects associated with a device, endpoint, or resource.
    Autonomous System (autonomous_system) [optional]: The Autonomous System details associated with an IP address.
    Domain (domain) [optional]: The name of the domain.
    Geo Location O (location) [optional]: The geographical location of the endpoint.
    Hardware Info (hw_info) [optional]: The endpoint hardware information.
    Hostname O (hostname) [recommended]: The fully qualified name of the endpoint.
    IP Address O (ip) [recommended]: The IP address of the endpoint, in either IPv4 or IPv6 format.
    Instance ID (instance_uid) [recommended]: The unique identifier of a VM instance.
    Intermediate IP Addresses O (intermediate_ips) [optional]: The intermediate IP Addresses.
    MAC Address O (mac) [optional]: The Media Access Control (MAC) address of the endpoint.
    Name (name) [recommended]: The short name of the endpoint.
    Network Interface ID (interface_uid) [recommended]: The unique identifier of the network interface.
    Network Interface Name (interface_name) [recommended]: The name of the network interface.
    Network Zone (zone) [optional]: The network zone or LAN segment.
    OS (os) [optional]: The endpoint operating system.
    Owner O (owner) [recommended]: The identity of the service or user account that owns the endpoint or was last logged into it.
    Port O (port) [recommended]: The port used for communication within the network connection.
    Proxy Endpoint O (proxy_endpoint) [optional]: The network proxy information pertaining to a specific endpoint.
    Service Name (svc_name) [recommended]: The service name in service-to-service connections.
    Subnet UID (subnet_uid) [optional]: The unique identifier of a virtual subnet.
    Type (type) [optional]: The network endpoint type.
    Type ID (type_id) [recommended]: The network endpoint type ID.
    Unique ID (uid) [recommended]: The unique identifier of the endpoint.
    VLAN (vlan_uid) [optional]: The Virtual LAN identifier.
    VPC UID (vpc_uid) [optional]: The unique identifier of the Virtual Private Cloud (VPC).
    """
    agent_list: List[Agent] = field(default_factory=list)
    autonomous_system: AutonomousSystem = field(default_factory=AutonomousSystem)
    domain: str = None
    location: GeoLocation = field(default_factory=GeoLocation)
    hw_info: DeviceHardwareInfo = field(default_factory=DeviceHardwareInfo)
    hostname: str = None
    ip: ipaddress.ip_address = None
    instance_uid: str = None
    intermediate_ips: List[ipaddress.ip_address] = field(default_factory=list)
    mac: str = None
    name: str = None
    interface_uid: str = None
    interface_name: str = None
    zone: str = None
    os: OperatingSystem = field(default_factory=OperatingSystem)
    owner: User = field(default_factory=User)
    port: int = None
    proxy_endpoint: NetworkProxyEndpoint = field(default_factory=NetworkProxyEndpoint)
    svc_name: str = None
    subnet_uid: str = None
    type: str = None
    type_id: NetworkTypeID = None
    uid: str = None
    vlan_uid: str = None
    vpc_uid: str = None


class BoundaryID(IntEnum):
    """
    The normalized identifier of the boundary of the connection.

    For cloud connections, this translates to the traffic-boundary (same VPC, through IGW, etc.). For traditional
    networks, this is described as Local, Internal, or External.
    """
    # The connection boundary is unknown.
    Unknown = 0
    # Local network traffic on the same endpoint.
    Localhost = 1
    # Internal network traffic between two endpoints inside network.
    Internal = 2
    # External network traffic between two endpoints on the Internet or outside the network.
    External = 3
    # Through another resource in the same VPC
    SameVPC = 4
    # Through an Internet gateway or a gateway VPC endpoint
    Internet_VPCGateway = 5
    # Through a virtual private gateway
    VirtualPrivateGateway = 6
    # Through an intra-region VPC peering connection
    IntraregionVPC = 7
    # Through an inter-region VPC peering connection
    InterregionVPC = 8
    # Through a local gateway
    LocalGateway = 9
    # Through a gateway VPC endpoint (Nitro-based instances only)
    GatewayVPC = 10
    # Through an Internet gateway (Nitro-based instances only)
    InternetGateway = 11
    # The boundary is not mapped. See the boundary attribute, which contains a data source specific value.
    Other = 99


class DirectionID(IntEnum):
    """
    The normalized identifier of the direction of the initiated connection, traffic, or email.
    """
    # The connection direction is unknown.
    Unknown = 0
    # Inbound network connection. The connection was originated from the Internet or outside network, destined for services on the inside network.
    Inbound = 1
    # Outbound network connection. The connection was originated from inside the network, destined for services on the Internet or outside network.
    Outbound = 2
    # Lateral network connection. The connection was originated from inside the network, destined for services on the inside network.
    Lateral = 3
    # The direction is not mapped. See the direction attribute, which contains a data source specific value.
    Other = 99


class ProtocolVersionID(IntEnum):
    """
    The Internet Protocol version identifier.
    """

    # The protocol version is unknown.
    Unknown = 0
    IPv4 = 4
    IPv6 = 6
    # The protocol version is not mapped. See the protocol_ver attribute, which contains a data source specific value.
    Other = 99


@dataclass
class NetworkConnectionInformation(BaseModel):
    """
    The Network Connection Information object describes characteristics of a network connection. Defined by
    D3FEND d3f:NetworkSession.

    Boundary (boundary) [optional]: The boundary of the connection, normalized to the caption of 'boundary_id'.
    Boundary ID (boundary_id) [recommended]: The normalized identifier of the boundary of the connection.
    Connection UID (uid) [recommended]: The unique identifier of the connection.
    Direction (direction) [optional]: The direction of the initiated connection, traffic, or email, normalized to the caption of the direction_id value.
    Direction ID (direction_id) [required]: The normalized identifier of the direction of the initiated connection, traffic, or email.
    IP Version (protocol_ver) [optional]: The Internet Protocol version.
    IP Version ID (protocol_ver_id) [recommended]: The Internet Protocol version identifier.
    Protocol Name (protocol_name) [recommended]: The TCP/IP protocol name in lowercase, as defined by the Internet Assigned Numbers Authority (IANA).
    Protocol Number (protocol_num) [recommended]: The TCP/IP protocol number, as defined by the Internet Assigned Numbers Authority (IANA).
    Session (session) [optional]: The authenticated user or service session.
    TCP Flags (tcp_flags) [optional]: The network connection TCP header flags (i.
    """
    boundary: str = None
    boundary_id: BoundaryID = None
    uid: str = None
    direction: str = None
    direction_id: DirectionID = None
    protocol_ver: str = None
    protocol_ver_id: ProtocolVersionID = None
    protocol_name: str = None
    protocol_num: int = None
    session: Session = field(default_factory=Session)
    tcp_flags: int = None
