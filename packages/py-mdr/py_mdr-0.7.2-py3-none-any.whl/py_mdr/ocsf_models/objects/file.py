from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List, Dict

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.digital_signature import DigitalSignature
from py_mdr.ocsf_models.objects.fingerprint import FingerPrint
from py_mdr.ocsf_models.objects.product import Product
from py_mdr.ocsf_models.objects.user import User


class ConfidentialityId(IntEnum):
    """
    he normalized identifier of the file content confidentiality indicator.
    """
    Unknown = 0
    NotConfidential = 1
    Confidential = 2
    Secret = 3
    TopSecret = 4
    Private = 5
    Restricted = 6
    Other = 99


@dataclass
class File(BaseModel):
    """
    The File object represents the metadata associated with a file stored in a computer system. It encompasses
    information about the file itself, including its attributes, properties, and organizational details.
    Defined by D3FEND d3f:File.

    Accessed Time (accessed_time) [optional]: The time when the file was last accessed.
    Accessor O (accessor) [optional]: The name of the user who last accessed the object.
    Attributes (attributes) [optional]: The bitmask value that represents the file attributes.
    Company Name (company_name) [optional]: The name of the company that published the file.
    Confidentiality (confidentiality) [optional]: The file content confidentiality, normalized to the confidentiality_id value.
    Confidentiality ID (confidentiality_id) [optional]: The normalized identifier of the file content confidentiality indicator.
    Created Time (created_time) [optional]: The time when the file was created.
    Creator O (creator) [optional]: The user that created the file.
    Description (desc) [optional]: The description of the file, as returned by file system.
    Digital Signature (signature) [optional]: The digital signature of the file.
    Extended Attributes (xattributes) [optional]: An unordered collection of zero or more name/value pairs where each pair represents a file or folder extended attribute.
    File Extension (ext) [recommended]: The extension of the file, excluding the leading dot.
    Hashes O (hashes) [recommended]: An array of hash attributes.
    MIME type (mime_type) [optional]: The Multipurpose Internet Mail Extensions (MIME) type of the file, if applicable.
    Modified Time (modified_time) [optional]: The time when the file was last modified.
    Modifier O (modifier) [optional]: The user that last modified the file.
    Name O (name) [required]: The name of the file.
    Owner O (owner) [optional]: The user that owns the file/object.
    Parent Folder (parent_folder) [optional]: The parent folder in which the file resides.
    Path (path) [recommended]: The full path to the file.
    Product (product) [optional]: The product that created or installed the file.
    Security Descriptor (security_descriptor) [optional]: The object security descriptor.
    Size (size) [optional]: The size of data, in bytes.
    System (is_system) [optional]: The indication of whether the object is part of the operating system.
    Type (type) [optional]: The file type.
    Type ID (type_id) [required]: The file type ID.
    Unique ID (uid) [optional]: The unique identifier of the file as defined by the storage system, such the file system file ID.
    Version (version) [optional]: The file version.
    """
    accessed_time: datetime = None
    accessor: User = None
    attributes: int = None
    company_name: str = None
    confidentiality: str = None
    confidentiality_id: ConfidentialityId = None
    created_time: datetime = None
    creator: User = None
    desc: str = None
    signature: DigitalSignature = field(default_factory=DigitalSignature)
    xattributes: List[Dict[str, str]] = field(default_factory=list)
    ext: str = None
    hashes: List[FingerPrint] = field(default_factory=list)
    mime_type: str = None
    modified_time: datetime = None
    modifier: User = field(default_factory=User)
    name: str = None
    owner: User = field(default_factory=User)
    parent_folder: str = None
    path: str = None
    product: Product = field(default_factory=Product)
    security_descriptor: str = None
    size: int = None
    is_system: bool = None
    type: str = None
    type_id: int = None
    uid: str = None
    version: str = None
