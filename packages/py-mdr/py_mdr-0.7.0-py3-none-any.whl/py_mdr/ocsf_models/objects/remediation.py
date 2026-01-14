from dataclasses import dataclass, field

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.kb_article import KBArticle


@dataclass
class Remediation(BaseModel):
    """
    Describes the remediation strategy for addressing findings, including detailed descriptions, related knowledgebase (KB) articles,
    and external references. This class supports comprehensive remediation planning and documentation.

    Attributes:
    - desc (str): Detailed description of the remediation strategy.
    - kb_article_list (list[KBArticle]): A list of KB articles describing patches or updates related to the remediation.
    - references (list[str]): URLs or references supporting the described remediation strategy.
    """

    desc: str = None
    kb_article_list: list[KBArticle] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
