from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List

from py_mdr.ocsf_models.events import CategoryUID, ClassUID, SeverityID, StatusID
from py_mdr.ocsf_models.events.base_event import BaseEvent
from py_mdr.ocsf_models.objects.actor import Actor
from py_mdr.ocsf_models.objects.device import Device
from py_mdr.ocsf_models.objects.enrichment import Enrichment
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.metadata import Metadata
from py_mdr.ocsf_models.objects.network import NetworkEndpoint
from py_mdr.ocsf_models.objects.observable import Observable


class EventLogActivityID(IntEnum):
    """
    The normalized identifier of the activity that triggered the event.
    """
    # The event activity is unknown.
    Unknown = 0
    # Clear the event log database, file, or cache.
    Clear = 1
    # Delete the event log database, file, or cache.
    Delete = 2
    # Export the event log database, file, or cache.
    Export = 3
    # Archive the event log database, file, or cache.
    Archive = 4
    # Rotate the event log database, file, or cache.
    Rotate = 5
    # Start the event logging service.
    Start = 6
    # Stop the event logging service.
    Stop = 7
    # Restart the event logging service.
    Restart = 8
    # Enable the event logging service.
    Enable = 9
    # Disable the event logging service.
    Disable = 10
    # The event activity is not mapped. See the activity_name attribute, which contains a data source specific value.
    Other = 99


class LogTypeID(IntEnum):
    """
    The normalized log type identifier.
    """
    # The log type is unknown.
    Unknown = 0
    # The log type is an Operating System log.
    OS = 1
    # The log type is an Application log.
    Application = 2
    # The log type is not mapped. See the log_type attribute, which contains a data source specific value.
    Other = 99


@dataclass
class EventLogActivity(BaseEvent):
    """
    Event Log Activity events report actions pertaining to the system's event logging service(s), such as disabling
    logging or clearing the log data.

    Activity (activity_name) [optional]: The event activity name, as defined by the activity_id.
    Activity ID (activity_id) [required]: The normalized identifier of the activity that triggered the event.
    Actor (actor) [recommended]: The actor that performed the activity.
    Category (category_name) [optional]: The event category name, as defined by category_uid value: System Activity.
    Category ID (category_uid) [required]: The category unique identifier of the event.
    Class (class_name) [optional]: The event class name, as defined by class_uid value: Event Log Activity.
    Class ID (class_uid) [required]: The unique identifier of a class.
    Count (count) [optional]: The number of times that events in the same logical group occurred during the event Start Time to End Time period.
    Destination Endpoint O (dst_endpoint) [recommended]: The
    Device O (device) [recommended]: The device that reported the event.
    Duration Milliseconds (duration) [optional]: The event duration or aggregate time, the amount of time the event covers from start_time to end_time in milliseconds.
    End Time (end_time) [optional]: The end time of a time period, or the time of the most recent event included in the aggregate event.
    Enrichments (enrichments) [optional]: The additional information from an external data source, which is associated with the event or a finding.
    Event Time (time) [required]: The normalized event occurrence time or the finding creation time.
    File O (file) [recommended]: The file
    Log Name (log_name) [recommended]: The name of the event log.
    Log Provider (log_provider) [recommended]: The logging provider or logging service
    Log Type (log_type) [recommended]: The log type, normalized to the caption of the log_type_id value.
    Log Type ID (log_type_id) [recommended]: The normalized log type identifier.
    Message (message) [recommended]: The description of the event/finding, as defined by the source.
    Metadata (metadata) [required]: The metadata associated with the event or a finding.
    Observables (observables) [recommended]: The observables associated with the event or a finding.
    Raw Data (raw_data) [optional]: The raw event/finding data as received from the source.
    Severity (severity) [optional]: The event/finding severity, normalized to the caption of the severity_id value.
    Severity ID (severity_id) [required]: The normalized identifier of the event/finding severity.
    Source Endpoint O (src_endpoint) [recommended]: The source endpoint for the event log activity.
    Start Time (start_time) [optional]: The start time of a time period, or the time of the least recent event included in the aggregate event.
    Status (status) [recommended]: The event status, normalized to the caption of the status_id value.
    Status Code (status_code) [recommended]: The event status code, as reported by the event source.
    Status Detail (status_detail) [recommended]: The status detail contains additional information about the event outcome.
    Status ID (status_id) [recommended]: The normalized identifier of the event status.
    Timezone Offset (timezone_offset) [recommended]: The number of minutes that the reported event time is ahead or behind UTC, in the range -1,080 to +1,080.
    Type ID (type_uid) [required]: The event/finding type ID.
    Type Name (type_name) [optional]: The event/finding type name, as defined by the type_uid.
    Unmapped Data (unmapped) [optional]: The attributes that are not mapped to the event schema.
    """
    activity_name: str = field(default=EventLogActivityID.Other.name)
    activity_id: EventLogActivityID = field(default=EventLogActivityID.Other)
    actor: Actor = field(default_factory=Actor)
    category_name: str = field(default=CategoryUID.SystemActivity.name)
    category_uid: int = field(default=CategoryUID.SystemActivity)
    class_name: str = field(default=ClassUID.EventLogActivity.name)
    class_uid: int = field(default=ClassUID.EventLogActivity)
    count: int = None
    dst_endpoint: NetworkEndpoint = field(default_factory=NetworkEndpoint)
    device: Device = field(default_factory=Device)
    duration: int = None
    end_time: datetime = None
    enrichments: List[Enrichment] = field(default_factory=list)
    time: datetime = None
    file: File = field(default_factory=File)
    log_name: str = None
    log_provider: str = None
    log_type: str = None
    log_type_id: LogTypeID = field(default=LogTypeID.Unknown)
    message: str = None
    metadata: Metadata = field(default_factory=Metadata)
    observables: List[Observable] = field(default_factory=list)
    raw_data: str = None
    severity: str = None
    severity_id: SeverityID = field(default=SeverityID.Unknown)
    src_endpoint: NetworkEndpoint = field(default_factory=NetworkEndpoint)
    start_time: datetime = None
    status: str = None
    status_code: str = None
    status_detail: str = None
    status_id: StatusID = field(default=StatusID.Unknown)
    timezone_offset: int = None
    # TODO: Set according to ActivityID
    type_uid: int = None
    type_name: str = None
    unmapped: object = None
