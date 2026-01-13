from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Author:
  id: str
  unique_id: str
  nickname: str
  sec_uid: str
  avatar_thumb: str
  avatar_medium: str
  avatar_larger: str
  verified: bool

@dataclass
class AuthorStats:
  follower_count: int
  following_count: int
  heart_count: int
  video_count: int

@dataclass
class Challenge:
  id: str
  title: str
  desc: str

@dataclass
class Music:
  id: str
  title: str
  author_name: str
  duration: int
  play_url: str
  cover_thumb: str
  cover_medium: str
  cover_large: str
  original: bool

@dataclass
class Video:
  id: str
  duration: int
  width: int
  height: int
  play_addr: str
  download_addr: str
  cover: str

@dataclass
class ItemStats:
  digg_count: int
  comment_count: int
  share_count: int
  play_count: int
  collect_count: int

@dataclass
class TextExtra:
  start: int
  end: int
  type: int
  user_id: Optional[str]
  user_unique_id: Optional[str]
  hashtag_name: Optional[str]

@dataclass
class SearchItem:
  id: str
  desc: str
  create_time: int
  author: Author
  author_stats: AuthorStats
  challenges: List[Challenge]
  text_extra: List[TextExtra]
  music: Optional[Music]
  video: Optional[Video]
  stats: ItemStats
  is_ad: bool

@dataclass
class LogPB:
  impr_id: str

@dataclass
class SearchVideoResponse:
  has_more: bool
  cursor: int
  log_pb: LogPB
  item_list: List[SearchItem]
