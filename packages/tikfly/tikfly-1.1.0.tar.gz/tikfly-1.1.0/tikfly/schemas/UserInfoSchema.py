from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class UserStats:
  diggCount: int
  followerCount: int
  followingCount: int
  friendCount: int
  heart: int
  heartCount: int
  videoCount: int

@dataclass
class UserStatsV2:
  diggCount: str
  followerCount: str
  followingCount: str
  friendCount: str
  heart: str
  heartCount: str
  videoCount: str

@dataclass
class BioLink:
  link: str
  risk: int

@dataclass
class CommerceUserInfo:
  commerceUser: bool
  downLoadLink: Dict[str, Any]
  category: str
  categoryButton: bool

@dataclass
class User:
  avatarLarger: str
  avatarMedium: str
  avatarThumb: str
  bioLink: BioLink
  canExpPlaylist: bool
  commentSetting: int
  commerceUserInfo: CommerceUserInfo
  downloadSetting: int
  duetSetting: int
  followingVisibility: int
  ftc: bool
  id: str
  isADVirtual: bool
  isEmbedBanned: bool
  nickNameModifyTime: int
  nickname: str
  openFavorite: bool
  privateAccount: bool
  profileEmbedPermission: int
  profileTab: Dict[str, Any]
  secUid: str
  secret: bool
  signature: str
  stitchSetting: int
  ttSeller: bool
  uniqueId: str
  verified: bool

@dataclass
class UserInfo:
  user: User
  stats: UserStats

@dataclass
class UserInfoResponse:
  statusCode: int
  userInfo: UserInfo