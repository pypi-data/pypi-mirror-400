from dataclasses import field, dataclass
from datetime import datetime
from enum import IntEnum
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.group import Group


class TypeID(IntEnum):
    """
    The normalized identifier of the database type.
    """
    # The type is unknown.
    Unknown = 0
    Relational = 1
    Network = 2
    ObjectOriented = 3
    Centralized = 4
    Operational = 5
    NoSQL = 6
    # The type is not mapped. See the type attribute, which contains a data source specific value.
    Other = 99


@dataclass
class Database(BaseModel):
    """
    The database object is used for databases which are typically datastore services that contain an organized
    collection of structured and unstructured data or a types of data.

    Created Time (created_time) [optional]: The time when the database was known to have been created.
    Description (desc) [optional]: The description of the database.
    Groups (groups) [optional]: The group names to which the database belongs.
    Modified Time (modified_time) [optional]: The most recent time when any changes, updates, or modifications were made within the database.
    Name (name) [recommended]: The database name, ordinarily as assigned by a database administrator.
    Size (size) [optional]: The size of the database in bytes.
    Type (type) [recommended]: The database type.
    Type ID (type_id) [required]: The normalized identifier of the database type.
    Unique ID (uid) [recommended]: The unique identifier of the database.
    """
    created_time: datetime = None
    desc: str = None
    groups: List[Group] = field(default_factory=list)
    modified_time: datetime = None
    name: str = None
    size: int = None
    type: str = None
    type_id: TypeID = None
    uid: str = None


class BucketTypeID(IntEnum):
    """
    The normalized identifier of the databucket type.
    """

    # The type is unknown.
    Unknown = 0
    S3 = 1
    AzureBlob = 2
    GCPBucket = 3
    # The type is not mapped. See the type attribute, which contains a data source specific value.
    Other = 99


@dataclass
class Databucket(BaseModel):
    """
    The databucket object is a basic container that holds data, typically organized through the use of data partitions.

    Created Time (created_time) [optional]: The time when the databucket was known to have been created.
    Description (desc) [optional]: The description of the databucket.
    File O (file) [optional]: A file within a databucket.
    Groups (groups) [optional]: The group names to which the databucket belongs.
    Modified Time (modified_time) [optional]: The most recent time when any changes, updates, or modifications were made within the databucket.
    Name (name) [recommended]: The databucket name.
    Size (size) [optional]: The size of the databucket in bytes.
    Type (type) [recommended]: The databucket type.
    Type ID (type_id) [required]: The normalized identifier of the databucket type.
    Unique ID (uid) [recommended]: The unique identifier of the databucket.
    """
    created_time: datetime = None
    desc: str = None
    file: File = field(default_factory=File)
    groups: List[Group] = field(default_factory=list)
    modified_time: datetime = None
    name: str = None
    size: int = None
    type: str = None
    type_id: BucketTypeID = None
    uid: str = None
