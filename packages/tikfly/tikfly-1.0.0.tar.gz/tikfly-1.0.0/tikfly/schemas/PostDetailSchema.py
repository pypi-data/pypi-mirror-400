from typing import List
from dataclasses import dataclass
from .UserInfoSchema import UserStats, UserStatsV2

@dataclass
class Video:
  id: str
  height: int
  width: int
  duration: int
  ratio: str
  cover: str
  originCover: str
  dynamicCover: str
  playAddr: str
  downloadAddr: str
  reflowCover: str
  bitrate: int
  encodedType: str
  format: str
  videoQuality: str
  encodeUserTag: str
  codecType: str
  size: str

@dataclass
class Author:
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
  createTime: int
  uniqueIdModifyTime: int
  nickNameModifyTime: int
  UserStoryStatus: int

class Music:
  album: str
  authorName: str
  coverLarge: str
  coverMedium: str
  coverThumb: str
  duration: int
  id: str
  isCopyrighted: bool
  original: bool
  playUrl: str
  private: bool
  title: str
  tt2dsp: dict

@dataclass
class Challenge:
  coverLarger: str
  coverMedium: str
  coverThumb: str
  desc: str
  id: str
  profileLarger: str
  profileMedium: str
  profileThumb: str
  title: str

@dataclass
class ItemStats:
  collectCount: int
  commentCount: int
  diggCount: int
  playCount: int
  shareCount: int

@dataclass
class ItemStatsV2:
  collectCount: str
  commentCount: str
  diggCount: str
  playCount: str
  repostCount: str
  shareCount: str

@dataclass
class ItemStruct:
  id: str
  desc: str
  createTime: str
  scheduleTime: int
  video: Video
  author: Author
  music: Music
  challenges: List[Challenge]
  stats: ItemStats
  statsV2: ItemStatsV2

  originalItem: bool
  officalItem: bool
  secret: bool
  forFriend: bool

  authorStats: UserStats
  authorStatsV2: UserStatsV2

  itemCommentStatus: int
  takeDown: int
  privateItem: bool
  duetEnabled: bool
  stitchEnabled: bool
  isAd: bool
  shareEnabled: bool
  duetDisplay: int
  stitchDisplay: int
  indexEnabled: bool
  adLabelVersion: int

  locationCreated: str
  BAInfo: str
  suggestedWords: List[str]
  CategoryType: int
  textLanguage: str
  textTranslatable: bool

@dataclass
class ItemInfo:
  itemStruct: ItemStruct

@dataclass
class PostDetailResponse:
  itemInfo: ItemInfo
  statusCode: int