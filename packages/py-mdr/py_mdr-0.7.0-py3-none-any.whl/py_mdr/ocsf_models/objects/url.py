from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from py_mdr.ocsf_models.objects.base_model import BaseModel


class WebsiteCategorizationID(IntEnum):
    """
    The Website categorization identifiers.
    """
    Unknown = 0
    # The Domain/URL category is unknown.
    Adult_MatureContent = 1
    Pornography = 3
    SexEducation = 4
    IntimateApparel_Swimsuit = 5
    Nudity = 6
    Extreme = 7
    Scam_Questionable_Illegal = 9
    Gambling = 11
    Violence_Hate_Racism = 14
    Weapons = 15
    Abortion = 16
    Hacking = 17
    Phishing = 18
    Entertainment = 20
    Business_Economy = 21
    AlternativeSpirituality_Belief = 22
    Alcohol = 23
    Tobacco = 24
    ControlledSubstances = 25
    ChildPornography = 26
    Education = 27
    CharitableOrganizations = 29
    Art_Culture = 30
    FinancialServices = 31
    Brokerage_Trading = 32
    Games = 33
    Government_Legal = 34
    Military = 35
    Political_SocialAdvocacy = 36
    Health = 37
    Technology_Internet = 38
    SearchEngines_Portals = 40
    MaliciousSources_Malnets = 43
    MaliciousOutboundData_Botnets = 44
    JobSearch_Careers = 45
    News_Media = 46
    Personals_Dating = 47
    Reference = 49
    MixedContent_PotentiallyAdult = 50
    Chat_IM_SMS = 51
    Email = 52
    Newsgroups_Forums = 53
    Religion = 54
    SocialNetworking = 55
    FileStorage_Sharing = 56
    RemoteAccessTools = 57
    Shopping = 58
    Auctions = 59
    RealEstate = 60
    Society_DailyLiving = 61
    PersonalSites = 63
    Restaurants_Dining_Food = 64
    Sports_Recreation = 65
    Travel = 66
    Vehicles = 67
    Humor_Jokes = 68
    SoftwareDownloads = 71
    Peer_to_Peer_P2P = 83
    Audio_VideoClips = 84
    Office_BusinessApplications = 85
    ProxyAvoidance = 86
    ForKids = 87
    WebAds_Analytics = 88
    WebHosting = 89
    Uncategorized = 90
    Suspicious = 92
    SexualExpression = 93
    Translation = 95
    Non_Viewable_Infrastructure = 96
    ContentServers = 97
    Placeholders = 98
    # The Domain/URL category is not mapped. See the categories attribute, which contains a data source specific value.
    Other = 99
    Spam = 101
    PotentiallyUnwantedSoftware = 102
    DynamicDNSHost = 103
    E_Card_Invitations = 106
    Informational = 107
    Computer_InformationSecurity = 108
    InternetConnectedDevices = 109
    InternetTelephony = 110
    OnlineMeetings = 111
    MediaSharing = 112
    Radio_AudioStreams = 113
    TV_VideoStreams = 114
    Piracy_CopyrightConcerns = 118
    Marijuana = 121


@dataclass
class UniformResourceLocator(BaseModel):
    """
    The Uniform Resource Locator(URL) object describes the characteristics of a URL. Defined in RFC 1738 and by D3FEND d3f:URL.

    Domain (domain) [optional]: The domain portion of the URL.
    HTTP Query String (query_string) [recommended]: The query portion of the URL.
    Hostname O (hostname) [recommended]: The URL host as extracted from the URL.
    Path (path) [recommended]: The URL path as extracted from the URL.
    Port O (port) [recommended]: The URL port.
    Resource Type (resource_type) [optional]: The context in which a resource was retrieved in a web request.
    Scheme (scheme) [recommended]: The scheme portion of the URL.
    Subdomain (subdomain) [optional]: The subdomain portion of the URL.
    URL String O (url_string) [recommended]: The URL string.
    Website Categorization (categories) [optional]: The Website categorization names, as defined by category_ids enum values.
    Website Categorization IDs (category_ids) [recommended]: The Website categorization identifiers.
    """
    domain: str = None
    query_string: str = None
    hostname: str = None
    path: str = None
    port: str = None
    resource_type: str = None
    scheme: str = None
    subdomain: str = None
    url_string: str = None
    categories: List[str] = field(default_factory=list)
    category_ids: List[WebsiteCategorizationID] = field(default_factory=list)
