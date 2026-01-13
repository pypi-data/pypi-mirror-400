from dataclasses import dataclass
from typing import List, Dict, Any

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
  UserStoryStatus: int

@dataclass
class AuthorStats:
  diggCount: int
  followerCount: int
  followingCount: int
  friendCount: int
  heart: int
  heartCount: int
  videoCount: int

@dataclass
class AuthorStatsV2:
  diggCount: str
  followerCount: str
  followingCount: str
  friendCount: str
  heart: str
  heartCount: str
  videoCount: str

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
class TextExtra:
  awemeId: str
  end: int
  hashtagName: str
  isCommerce: bool
  secUid: str
  start: int
  subType: int
  type: int
  userId: str
  userUniqueId: str

@dataclass
class Content:
  desc: str
  textExtra: List[TextExtra]

@dataclass
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
  tt2dsp: Dict[str, Any]

@dataclass
class ItemControl:
  can_repost: bool

@dataclass
class Stats:
  collectCount: int
  commentCount: int
  diggCount: int
  playCount: int
  shareCount: int

@dataclass
class StatsV2:
  collectCount: str
  commentCount: str
  diggCount: str
  playCount: str
  repostCount: str
  shareCount: str

@dataclass
class PlayAddr:
  DataSize: int
  FileCs: str
  FileHash: str
  Height: int
  Uri: str
  UrlKey: str
  UrlList: List[str]
  Width: int

@dataclass
class BitrateInfo:
  Bitrate: int
  BitrateFPS: int
  CodecType: str
  Format: str
  GearName: str
  MVMAF: str
  PlayAddr: PlayAddr
  QualityType: int
  VideoExtra: str

@dataclass
class Video:
  PlayAddrStruct: PlayAddr
  VQScore: str
  bitrate: int
  bitrateInfo: List[BitrateInfo]
  codecType: str
  cover: str
  definition: str
  downloadAddr: str
  duration: int
  dynamicCover: str
  encodedType: str
  format: str
  height: int
  id: str
  originCover: str
  playAddr: str
  ratio: str
  size: int
  videoID: str
  videoQuality: str
  width: int

@dataclass
class VideoItem:
  AIGCDescription: str
  CategoryType: int
  author: Author
  authorStats: AuthorStats
  authorStatsV2: AuthorStatsV2
  backendSourceEventTracking: str
  challenges: List[Challenge]
  contents: List[Content]
  createTime: int
  desc: str
  diversificationId: int
  duetDisplay: int
  duetEnabled: bool
  forFriend: bool
  id: str
  isAd: bool
  isReviewing: bool
  itemCommentStatus: int
  item_control: ItemControl
  music: Music
  officalItem: bool
  originalItem: bool
  privateItem: bool
  secret: bool
  shareEnabled: bool
  stats: Stats
  statsV2: StatsV2
  stitchDisplay: int
  stitchEnabled: bool
  textExtra: List[TextExtra]
  textLanguage: str
  textTranslatable: bool
  video: Video

@dataclass
class UserPostResponse:
  cursor: str
  hasMore: bool
  itemList: List[VideoItem]
