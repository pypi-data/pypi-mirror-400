from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AvatarThumb:
  uri: str
  url_list: List[str]
  width: int
  height: int
  url_prefix: Optional[str]

@dataclass
class UserInfo:
  uid: str
  nickname: str
  signature: str
  avatar_thumb: AvatarThumb
  follower_count: int
  total_favorited: int
  custom_verify: str
  unique_id: str
  sec_uid: str
  room_id: int
  room_id_str: str
  enterprise_verify_reason: Optional[str]
  followers_detail: Optional[dict]
  platform_sync_info: Optional[dict]
  geofencing: Optional[dict]
  cover_url: Optional[str]
  item_list: Optional[list]
  type_label: Optional[str]
  ad_cover_url: Optional[str]
  relative_users: Optional[list]
  cha_list: Optional[list]
  need_points: Optional[int]
  homepage_bottom_toast: Optional[dict]
  can_set_geofencing: Optional[bool]
  white_cover_url: Optional[str]
  user_tags: Optional[list]
  bold_fields: Optional[list]
  search_highlight: Optional[dict]
  mutual_relation_avatars: Optional[list]
  events: Optional[list]
  advance_feature_item_order: Optional[list]
  advanced_feature_info: Optional[dict]
  user_profile_guide: Optional[dict]
  shield_edit_field_info: Optional[dict]
  can_message_follow_status_list: Optional[list]
  account_labels: Optional[list]

@dataclass
class UserListItem:
  user_info: UserInfo
  position: Optional[int]
  uniqid_position: Optional[int]
  effects: Optional[list]
  musics: Optional[list]
  items: Optional[list]
  mix_list: Optional[list]
  challenges: Optional[list]

@dataclass
class LogPB:
  impr_id: str

@dataclass
class SearchAccountResponse:
  hasMore: int
  cursor: int
  log_pb: LogPB
  user_list: List[UserListItem]