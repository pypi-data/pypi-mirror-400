from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.product import Product


@dataclass
class CWE(BaseModel):
    """
    The CWE object represents a weakness in a software system that can be exploited by a threat actor to perform an
    attack. The CWE object is based on the Common Weakness Enumeration (CWE) catalog.

    CWE ID (uid) [required]: The Common Weakness Enumeration unique number assigned to a specific weakness.
    Caption (caption) [optional]: The caption assigned to the Common Weakness Enumeration unique identifier.
    Source URL (src_url) [optional]: URL pointing to the CWE Specification.
    """
    uid: str = None
    caption: str = None
    src_url: str = None


@dataclass
class Metric(BaseModel):
    """
    The Metric object defines a simple name/value pair entity for a metric.
    """
    name: str = None
    value: str = None


@dataclass
class CVSS(BaseModel):
    """
    The Common Vulnerability Scoring System (CVSS) object provides a way to capture the principal characteristics of a
    vulnerability and produce a numerical score reflecting its severity.

    Base Score (base_score) [required]: The CVSS base score.
    CVSS Depth (depth) [recommended]: The CVSS depth represents a depth of the equation used to calculate CVSS score.
    Metrics (metrics) [optional]: The Common Vulnerability Scoring System metrics.
    Overall Score (overall_score) [recommended]: The CVSS overall score, impacted by base, temporal, and environmental metrics.
    Severity (severity) [optional]: The Common Vulnerability Scoring System (CVSS) Qualitative Severity Rating.
    Vector String (vector_string) [optional]: The CVSS vector string is a text representation of a set of CVSS metrics.
    Version (version) [required]: The CVSS version.
    """
    base_score: float = None
    depth: str = None
    metrics: List[Metric] = field(default_factory=list)
    overall_score: float = None
    severity: str = None
    vector_string: str = None
    version: str = None


@dataclass
class EPSS(BaseModel):
    """
    The Exploit Prediction Scoring System (EPSS) object describes the estimated probability a vulnerability will be
    exploited. EPSS is a community-driven effort to combine descriptive information about vulnerabilities (CVEs) with
    evidence of actual exploitation in-the-wild.
    """
    created_time: datetime = None
    score: str = None
    percentile: float = None
    version: str = None


@dataclass
class CVE(BaseModel):
    """
    The Common Vulnerabilities and Exposures (CVE) object represents publicly disclosed cybersecurity vulnerabilities
    defined in CVE Program catalog (CVE). There is one CVE Record for each vulnerability in the catalog.

    CVE ID O (uid) [required]: The Common Vulnerabilities and Exposures unique number assigned to a specific computer vulnerability.
    CVSS Score (cvss) [recommended]: The CVSS object details Common Vulnerability Scoring System (CVSS) scores from the advisory that are related to the vulnerability.
    CWE (cwe) [optional]: The CWE object represents a weakness in a software system that can be exploited by a threat actor to perform an attack.
    CWE UID (cwe_uid) [optional]: The Common Weakness Enumeration (CWE) unique identifier.
    CWE URL O (cwe_url) [optional]: Common Weakness Enumeration (CWE) definition URL.
    Created Time (created_time) [recommended]: The Record Creation Date identifies when the CVE ID was issued to a CVE Numbering Authority (CNA) or the CVE Record was published on the CVE List.
    Description (desc) [optional]: A brief description of the CVE Record.
    EPSS (epss) [optional]: The Exploit Prediction Scoring System (EPSS) object describes the estimated probability a vulnerability will be exploited.
    Modified Time (modified_time) [optional]: The Record Modified Date identifies when the CVE record was last updated.
    Product (product) [optional]: The product where the vulnerability was discovered.
    References (references) [recommended]: A list of reference URLs with additional information about the CVE Record.
    Title (title) [recommended]: A title or a brief phrase summarizing the CVE record.
    Vulnerability Type (type) [recommended]: The vulnerability type as selected from a large dropdown menu during CVE refinement.
    """
    uid: str = None
    cvss: List[CVSS] = field(default_factory=CVSS)
    cwe: CWE = field(default_factory=CWE)
    cwe_uid: str = None
    cwe_url: str = None
    created_time: datetime = None
    desc: str = None
    epss: EPSS = field(default_factory=EPSS)
    modified_time: datetime = None
    product: Product = field(default_factory=Product)
    references: List[str] = field(default_factory=list)
    title: str = None
    type: str = None
