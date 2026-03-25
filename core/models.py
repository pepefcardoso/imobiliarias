from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Property:
    agency: str
    title: str
    url: str
    price: Optional[float] = field(default=None)
    area: Optional[float] = field(default=None)
    bedrooms: Optional[int] = field(default=None)
    bathrooms: Optional[int] = field(default=None)
    parking: Optional[int] = field(default=None)
    neighborhood: Optional[str] = field(default=None)
    city: Optional[str] = field(default=None)
    image_url: Optional[str] = field(default=None)
    latitude: Optional[float] = field(default=None)
    longitude: Optional[float] = field(default=None)
    source_links: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "agency": self.agency,
            "title": self.title,
            "url": self.url,
            "price": self.price,
            "area": self.area,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "parking": self.parking,
            "neighborhood": self.neighborhood,
            "city": self.city,
            "image_url": self.image_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "source_links": self.source_links,
        }

@dataclass
class SearchQuery:
    city: Optional[str] = field(default=None)
    neighborhood: Optional[str] = field(default=None)
    min_price: Optional[float] = field(default=None)
    max_price: Optional[float] = field(default=None)
    min_bedrooms: Optional[int] = field(default=None)
    min_bathrooms: Optional[int] = field(default=None)
    min_parking: Optional[int] = field(default=None)
    min_area: Optional[float] = field(default=None)
    max_area: Optional[float] = field(default=None)