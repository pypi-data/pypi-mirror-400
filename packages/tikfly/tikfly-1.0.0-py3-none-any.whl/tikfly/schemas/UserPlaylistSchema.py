from typing import List
from dataclasses import dataclass

@dataclass
class Creator:
  avatarLarger: str
  avatarMedium: str
  avatarThumb: str
  commentSetting: int
  downloadSetting: int
  duetSetting: int
  ftc: bool
  id: str
  isADVirtual: bool
  nickname: str
  openFavorite: bool
  privateAccount: bool
  secUid: str
  secret: bool
  signature: str
  stitchSetting: int
  ttSeller: bool
  uniqueId: str
  verified: bool

@dataclass
class PlayListItem:
  cover: str
  creator: Creator
  id: str
  mixId: str
  mixName: str
  name: str
  videoCount: int

@dataclass
class UserPlaylistResponse:
  cursor: str
  hasMore: bool
  playList: List[PlayListItem]