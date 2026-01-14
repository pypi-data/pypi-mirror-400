from dataclasses import dataclass, field
from datetime import datetime

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.operating_system import OperatingSystem
from py_mdr.ocsf_models.objects.product import Product


@dataclass
class KBArticle(BaseModel):
    """
    Describes a knowledgebase article, providing essential information such as its classification,
    release date, applicable operating system, and severity. It includes details like the article's
    size, source URL, and whether it has been superseded by another patch.

    Attributes:
    - classification: Vendor's classification of the KB article.
    - created_time: Time the KB article was created.
    - created_time_dt: Time the KB article was created in datetime
    - os: Operating system the KB article applies to.
    - bulletin: Bulletin identifier of the KB article.
    - product: Product details the KB article applies to.
    - severity: Severity rating of the KB article.
    - size: Size of the KB article in bytes.
    - src_url: Link to the KB article from the vendor.
    - is_superseded: Indicates if the article has been replaced by another.
    - title: Title of the KB article.
    - uid: Unique identifier for the KB article.
    """

    classification: str = None
    created_time: int = None
    created_time_dt: datetime = None
    os: OperatingSystem = field(default_factory=OperatingSystem)
    bulletin: str = None
    product: Product = field(default_factory=Product)
    severity: str = None
    size: int = None
    src_url: str = None
    is_superseded: bool = None
    title: str = None
    uid: str = None
