from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from py_mdr.ocsf_models.events import CategoryUID, SeverityID, StatusID, ClassUID
from py_mdr.ocsf_models.events.base_event import BaseEvent
from py_mdr.ocsf_models.events.discovery import ActivityID
from py_mdr.ocsf_models.objects.actor import Actor
from py_mdr.ocsf_models.objects.device import Device
from py_mdr.ocsf_models.objects.enrichment import Enrichment
from py_mdr.ocsf_models.objects.metadata import Metadata
from py_mdr.ocsf_models.objects.observable import Observable
from py_mdr.ocsf_models.objects.product import Product
from py_mdr.ocsf_models.objects.software_package import SoftwarePackage


@dataclass
class SoftwareInventoryInfo(BaseEvent):
    """
    Software Inventory Info events report device software inventory data that is either logged or proactively collected.
    For example, when collecting device information from a CMDB or running a network sweep of connected devices.

    Activity (activity_name) [optional]: The event activity name, as defined by the activity_id.
    Activity ID (activity_id) [required]: The normalized identifier of the activity that triggered the event.
    Actor (actor) [optional]: The actor object describes details about the user/role/process that was the source of the activity.
    Category (category_name) [optional]: The event category name, as defined by category_uid value: Discovery.
    Category ID (category_uid) [required]: The category unique identifier of the event.
    Class (class_name) [optional]: The event class name, as defined by class_uid value: Software Inventory Info.
    Class ID (class_uid) [required]: The unique identifier of a class.
    Count (count) [optional]: The number of times that events in the same logical group occurred during the event Start Time to End Time period.
    Device O (device) [required]: The device that is being discovered by an inventory process.
    Duration Milliseconds (duration) [optional]: The event duration or aggregate time, the amount of time the event covers from start_time to end_time in milliseconds.
    End Time (end_time) [optional]: The end time of a time period, or the time of the most recent event included in the aggregate event.
    Enrichments (enrichments) [optional]: The additional information from an external data source, which is associated with the event or a finding.
    Event Time (time) [required]: The normalized event occurrence time or the finding creation time.
    Message (message) [recommended]: The description of the event/finding, as defined by the source.
    Metadata (metadata) [required]: The metadata associated with the event or a finding.
    Observables (observables) [recommended]: The observables associated with the event or a finding.
    Product (product) [optional]: Additional product attributes that have been discovered or enriched from a catalog or other external source.
    Raw Data (raw_data) [optional]: The raw event/finding data as received from the source.
    Severity (severity) [optional]: The event/finding severity, normalized to the caption of the severity_id value.
    Severity ID (severity_id) [required]: The normalized identifier of the event/finding severity.
    Software Package (package) [required]: The device software that is being discovered by an inventory process.
    Start Time (start_time) [optional]: The start time of a time period, or the time of the least recent event included in the aggregate event.
    Status (status) [recommended]: The event status, normalized to the caption of the status_id value.
    Status Code (status_code) [recommended]: The event status code, as reported by the event source.
    Status Detail (status_detail) [recommended]: The status detail contains additional information about the event/finding outcome.
    Status ID (status_id) [recommended]: The normalized identifier of the event status.
    Timezone Offset (timezone_offset) [recommended]: The number of minutes that the reported event time is ahead or behind UTC, in the range -1,080 to +1,080.
    Type ID (type_uid) [required]: The event/finding type ID.
    Type Name (type_name) [optional]: The event/finding type name, as defined by the type_uid.
    Unmapped Data (unmapped) [optional]: The attributes that are not mapped to the event schema.
    """
    activity_name: str = None
    activity_id: ActivityID = None
    actor: Actor = field(default_factory=Actor)
    category_name: str = field(default=CategoryUID.Discovery.name)
    category_uid: CategoryUID = field(default=CategoryUID.Discovery)
    class_name: str = field(default=ClassUID.SoftwareInventoryInfo.name)
    class_uid: ClassUID = field(default=ClassUID.SoftwareInventoryInfo)
    count: int = None
    device: Device = field(default_factory=Device)
    duration: int = None
    end_time: datetime = None
    enrichments: List[Enrichment] = field(default_factory=list)
    time: datetime = None
    message: str = None
    metadata: Metadata = field(default_factory=Metadata)
    observables: List[Observable] = field(default_factory=list)
    product: Product = field(default_factory=Product)
    raw_data: str = None
    severity: str = None
    severity_id: SeverityID = None
    package: SoftwarePackage = field(default_factory=SoftwarePackage)
    start_time: datetime = None
    status: str = None
    status_code: str = None
    status_detail: str = None
    status_id: StatusID = None
    timezone_offset: int = None
    # TODO: Add uid calculation (class_uid * 100 + activity_id)
    type_uid: int = None
    type_name: str = None
    unmapped: object = None
