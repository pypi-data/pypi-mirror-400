from dataclasses import dataclass

@dataclass
class Challenge:
  id: str
  title: str
  desc: str
  coverLarger: str
  coverMedium: str
  coverThumb: str
  profileLarger: str
  profileMedium: str
  profileThumb: str

@dataclass
class ChallengeAnnouncement:
  title: str
  body: str

@dataclass
class ChallengeStats:
  videoCount: int
  viewCount: int

@dataclass
class ChallengeStatsV2:
  videoCount: str
  viewCount: str

@dataclass
class ChallengeInfo:
  challenge: Challenge
  challengeAnnouncement: ChallengeAnnouncement
  stats: ChallengeStats
  statsV2: ChallengeStatsV2

@dataclass
class ChallengeInfoResponse:
  challengeInfo: ChallengeInfo
  statusCode: int