from dataclasses import dataclass, field
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class Group(BaseModel):
    """
    The Group object represents a collection or association of entities, such as users, policies, or devices. It
    serves as a logical grouping mechanism to organize and manage entities with similar characteristics or permissions
    within a system or organization.

    Account Type (type) [optional]: The type of the group or account.
    Description (desc) [optional]: The group description.
    Domain (domain) [optional]: The domain where the group is defined.
    Name (name) [recommended]: The group name.
    Privileges (privileges) [optional]: The group privileges.
    Unique ID (uid) [recommended]: The unique identifier of the group.
    """
    type: str = None
    desc: str = None
    domain: str = None
    name: str = None
    privileges: List[str] = field(default_factory=list)
    uid: str = None


@dataclass
class Policy(BaseModel):
    """
    The Policy object describes the policies that are applicable.

    Policy attributes provide traceability to the operational state of the security product at the time that the
    event was captured, facilitating forensics, troubleshooting, and policy tuning/adjustments.

    Applied (is_applied) [recommended]: A determination if the content of a policy was applied to a target or request, or not.
    Description (desc) [optional]: The description of the policy.
    Group (group) [optional]: The policy group.
    Name (name) [recommended]: The policy name.
    Unique ID (uid) [recommended]: A unique identifier of the policy instance.
    Version (version) [recommended]: The policy version number.
    """
    is_applied: bool = None
    desc: str = None
    group: Group = field(default_factory=Group)
    name: str = None
    uid: str = None
    version: str = None


@dataclass
class AuthorizationResult(BaseModel):
    """
    The Authorization Result object provides details about the authorization outcome and associated policies related
    to activity.

    Authorization Decision/Outcome (decision) [recommended]: Authorization Result/outcome, e.
    Policy (policy) [optional]: Details about the Identity/Access management policies that are applicable.
    """
    decision: str = None
    policy: Policy = field(default_factory=Policy)
