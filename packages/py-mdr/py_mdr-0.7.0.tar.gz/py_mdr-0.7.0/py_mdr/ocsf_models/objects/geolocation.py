from dataclasses import dataclass, field

from py_mdr.ocsf_models.objects.base_model import BaseModel


@dataclass
class GeoLocation(BaseModel):
    """
    The GeoLocation object encapsulates geographical information about a specific location. This includes details that can be used to pinpoint a location globally, identify regional characteristics, and provide additional context about the environment of the location.

    Attributes:
    - City (city) [Recommended]: Name of the city for the location.
    - Continent (continent) [Recommended]: Name of the continent where the location is situated.
    - Coordinates (coordinates) [Recommended]: A longitude/latitude pair conforming to GeoJSON format.
    - Country (country) [Recommended]: ISO 3166-1 Alpha-2 country code, capitalized.
    - Description (desc) [Optional]: A description of the geographical location.
    - ISP (isp) [Optional]: Internet Service Provider associated with the location.
    - On Premises (is_on_premises) [Optional]: Indicates if the location is on premises.
    - Postal Code (postal_code) [Optional]: Postal code for the location.
    - Provider (provider) [Optional]: Provider of the geographical data.
    - Region (region) [Optional]: The principal subdivision of the country, such as a state or province.
    """

    city: str = None
    continent: str = None
    coordinates: list[float] = field(default_factory=list)
    country: str = None
    desc: str = None
    isp: str = None
    is_on_premises: bool = None
    postal_code: str = None
    provider: str = None
    region: str = None
