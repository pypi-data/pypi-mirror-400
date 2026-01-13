from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PoiPhoneInfo:
  exist: bool

@dataclass
class PoiPictureAlbum:
  totalCount: int

@dataclass
class PoiDetailTag:
  content: str
  tagType: int

@dataclass
class Poi:
  id: str
  name: str
  address: str
  category: str
  type: int
  typeCode: str
  city: str
  cityCode: str
  province: str
  country: str
  countryCode: str
  fatherPoiId: str
  fatherPoiName: str
  ttTypeCode: str
  ttTypeNameTiny: str
  ttTypeNameMedium: str
  ttTypeNameSuper: str
  indexEnabled: bool
  isClaimed: bool
  isCollected: bool
  phoneInfo: PoiPhoneInfo
  pictureAlbum: PoiPictureAlbum
  poiDetailTags: List[PoiDetailTag]
  allLevelGeoPoiInfo: Dict[str, Any]

@dataclass
class PoiStats:
  videoCount: int

@dataclass
class PoiInfo:
  poi: Poi
  stats: PoiStats

@dataclass
class PlaceInfoResponse:
  poiInfo: PoiInfo