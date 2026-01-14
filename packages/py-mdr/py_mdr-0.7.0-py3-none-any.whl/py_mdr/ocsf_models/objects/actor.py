from dataclasses import dataclass, field
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.policy import AuthorizationResult
from py_mdr.ocsf_models.objects.process import IdentityProvider, Process, Session
from py_mdr.ocsf_models.objects.user import User


@dataclass
class Actor(BaseModel):
    """
    The Actor object contains details about the user, role, application, service, or process that initiated or
    performed a specific activity.

    Application ID (app_uid) [optional]: The unique identifier of the client application or service that initiated the activity.
    Application Name (app_name) [optional]: The client application or service that initiated the activity.
    Authorization Information (authorizations) [optional]: Provides details about an authorization, such as authorization outcome, and any associated policies related to the activity/event.
    Identity Provider (idp) [optional]: This object describes details about the Identity Provider used.
    Process (process) [recommended]: The process that initiated the activity.
    Session (session) [optional]: The user session from which the activity was initiated.
    User (user) [recommended]: The user that initiated the activity or the user context from which the activity was initiated.
    """
    app_uid: str = None
    app_name: str = None
    authorizations: List[AuthorizationResult] = field(default_factory=AuthorizationResult)
    idp: IdentityProvider = field(default_factory=IdentityProvider)
    process: Process = field(default_factory=Process)
    session: Session = field(default_factory=Session)
    user: User = field(default_factory=User)
