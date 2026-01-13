from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MusicArtist:
  id: str
  uniqueId: str
  nickname: str
  secUid: str
  signature: str
  avatarLarger: str
  avatarMedium: str
  avatarThumb: str
  ftc: bool
  openFavorite: bool
  privateAccount: bool
  secret: bool

@dataclass
class Music:
  id: str
  title: str
  authorName: str
  album: str
  coverLarge: str
  coverMedium: str
  coverThumb: str
  duration: int
  playUrl: str
  original: bool
  private: bool
  isCopyrighted: bool
  tt2dsp: Dict[str, Any]

@dataclass
class MusicStats:
  videoCount: int

@dataclass
class MusicInfo:
  artist: MusicArtist
  artists: List[MusicArtist]
  music: Music
  stats: MusicStats

@dataclass
class MusicInfoData:
  musicInfo: MusicInfo

@dataclass
class MusicInfoResponse:
  data: MusicInfoData
