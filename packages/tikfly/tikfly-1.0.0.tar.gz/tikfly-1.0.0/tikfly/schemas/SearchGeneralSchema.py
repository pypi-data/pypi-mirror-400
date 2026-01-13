from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Author:
  id: str
  unique_id: str
  nickname: str
  avatar_thumb: Optional[str]
  avatar_medium: Optional[str]
  avatar_larger: Optional[str]
  verified: bool
  signature: Optional[str]
  sec_uid: Optional[str]

@dataclass
class AuthorStats:
  follower_count: int
  following_count: int
  heart_count: int
  video_count: int

@dataclass
class Music:
  id: str
  title: str
  author_name: str
  duration: int
  play_url: str
  cover_thumb: Optional[str]

@dataclass
class Video:
  id: str
  duration: int
  width: int
  height: int
  play_addr: str
  download_addr: Optional[str]
  cover: Optional[str]

@dataclass
class VideoStats:
  play_count: int
  digg_count: int
  comment_count: int
  share_count: int

@dataclass
class VideoItem:
  id: str
  desc: str
  create_time: int
  author: Author
  author_stats: AuthorStats
  music: Optional[Music]
  video: Video
  stats: VideoStats

@dataclass
class SearchItem:
  type: int
  item: VideoItem

@dataclass
class LogPB:
  impr_id: str

@dataclass
class SearchGeneralResponse:
  has_more: bool
  cursor: int
  log_pb: LogPB
  items: List[SearchItem]