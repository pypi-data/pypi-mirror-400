from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class EffectIconUrl:
  uri: str
  url_list: List[str]
  url_prefix: Optional[str]

@dataclass
class StickerInfo:
  id: str
  effect_id: str
  name: str
  desc: str
  effect_source: int
  publish_time: int
  owner_id: str
  owner_nickname: str
  owner_verified_type: int
  sec_uid: str
  is_top_effect_designer: bool
  user_count: int
  vv_count: int
  tags: List[str]
  children: List[Any]
  extra: str
  icon_url: EffectIconUrl
  attributions: Optional[Any]
  linked_anchors: Optional[Any]

@dataclass
class EffectInfoResponse:
  sticker_infos: List[StickerInfo]

