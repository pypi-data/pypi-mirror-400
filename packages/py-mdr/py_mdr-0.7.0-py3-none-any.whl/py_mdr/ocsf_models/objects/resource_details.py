from dataclasses import dataclass, field
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.group import Group
from py_mdr.ocsf_models.objects.user import User


@dataclass
class ResourceDetails(BaseModel):
    """
    The Resource Details object describes details about resources that were affected by the activity/event.

    Attributes:
    - Criticality (criticality) [Optional]: The criticality of the resource as defined by the event source.
    - Data (data) [Optional]: Additional data describing the resource.
    - Group (group) [Optional]: The name of the related resource group.
    - Labels (labels) [Optional]: The list of labels/tags associated to a resource.
    - Name (name) [Optional]: The name of the resource.
    - Namespace (namespace) [Optional]: The namespace is useful when similar entities exist that you need to keep separate.
    - Owner (owner) [Recommended]: The identity of the service or user account that owns the resource.
    - Type (type) [Optional]: The resource type as defined by the event source.
    - Unique ID (uid) [Optional]: The unique identifier of the resource.
    - Version (version) [Optional]: The version of the resource. For example 1.2.3.

    If Cloud profile:
    - Cloud Partition (cloud_partition) [Optional]: The canonical cloud partition name to which the region is assigned (e.g. AWS Partitions: aws, aws-cn, aws-us-gov).
    - Region (region) [Optional]: The cloud region of the resource.
    """

    cloud_partition: str = None
    region: str = None
    criticality: str = None
    data: dict[str, object] = field(default_factory=dict)
    group: Group = field(default_factory=Group)
    labels: List[str] = field(default_factory=list)
    name: str = None
    namespace: str = None
    owner: User = field(default_factory=User)
    type: str = None
    uid: str = None
    version: str = None
