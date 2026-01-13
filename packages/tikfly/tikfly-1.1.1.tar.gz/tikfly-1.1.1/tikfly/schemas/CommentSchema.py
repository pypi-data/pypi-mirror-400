from dataclasses import dataclass
from typing import List, Any, Optional

@dataclass
class AvatarThumb:
  uri: str
  url_list: List[str]
  url_prefix: Optional[str]

@dataclass
class CommentUser:
  uid: str
  sec_uid: str
  unique_id: str
  nickname: str
  avatar_thumb: AvatarThumb
  custom_verify: str
  enterprise_verify_reason: str
  account_labels: Optional[Any]
  ad_cover_url: Optional[Any]
  advance_feature_item_order: Optional[Any]
  advanced_feature_info: Optional[Any]
  bold_fields: Optional[Any]
  can_message_follow_status_list: Optional[Any]
  can_set_geofencing: Optional[Any]
  cha_list: Optional[Any]
  cover_url: Optional[Any]
  events: Optional[Any]
  followers_detail: Optional[Any]
  geofencing: Optional[Any]
  homepage_bottom_toast: Optional[Any]
  item_list: Optional[Any]
  mutual_relation_avatars: Optional[Any]
  need_points: Optional[Any]
  platform_sync_info: Optional[Any]
  relative_users: Optional[Any]
  search_highlight: Optional[Any]
  shield_edit_field_info: Optional[Any]
  type_label: Optional[Any]
  user_profile_guide: Optional[Any]
  user_tags: Optional[Any]
  white_cover_url: Optional[Any]

@dataclass
class SortExtraScore:
  reply_score: float
  show_more_score: float

@dataclass
class Comment:
  cid: str
  aweme_id: str
  text: str
  comment_language: str
  create_time: int
  digg_count: int
  collect_stat: int
  reply_comment_total: int
  reply_id: str
  reply_to_reply_id: str
  allow_download_photo: bool
  author_pin: bool
  is_author_digged: bool
  is_comment_translatable: bool
  is_high_purchase_intent: bool
  status: int
  stick_position: int
  sort_extra_score: SortExtraScore
  user: CommentUser

@dataclass
class CommentListResponse:
  hasMore: int
  cursor: int
  total: int
  comments: List[Comment]