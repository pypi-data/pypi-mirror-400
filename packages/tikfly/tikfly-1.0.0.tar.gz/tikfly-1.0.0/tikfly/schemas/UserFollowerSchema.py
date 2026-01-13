from typing import List
from dataclasses import dataclass
from .UserInfoSchema import UserStats, UserStatsV2

@dataclass
class UserProfile:
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
class UserListItem:
  stats: UserStats
  statsV2: UserStatsV2
  user: UserProfile

@dataclass
class UserFollowerResponse:
  hasMore: bool
  minCursor: int
  total: int
  userList: List[UserListItem]
