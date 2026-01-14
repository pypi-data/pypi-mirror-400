from dataclasses import dataclass, field

from py_mdr.ocsf_models.objects.account import Account
from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.organization import Organization


@dataclass
class Cloud(BaseModel):
    """
    The Cloud object contains information about a cloud account such as AWS Account ID, regions, etc.

    Attributes:
    - Account (account) [Optional]: The account object describes details about the account that was the source or target of the activity.
    - Network Zone (zone) [Optional]: The availability zone in the cloud region, as defined by the cloud provider.
    - Organization (org) [Optional]: Organization and org unit relevant to the event or object.
    - Project ID (project_uid) [Optional]: The unique identifier of a Cloud project.
    - Provider (provider) [Required]: The unique name of the Cloud services provider, such as AWS, MS Azure, GCP, etc.
    - Region (region) [Recommended]: The name of the cloud region, as defined by the cloud provider.
    """

    account: Account = field(default_factory=Account)
    zone: str = None
    org: Organization = field(default_factory=Organization)
    project_uid: str = None
    provider: str = None
    region: str = None
