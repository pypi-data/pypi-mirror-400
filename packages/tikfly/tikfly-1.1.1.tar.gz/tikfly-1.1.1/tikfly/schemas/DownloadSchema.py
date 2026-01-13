from dataclasses import dataclass

@dataclass
class DownloadVideoResponse:
  play: str
  play_watermark: str

@dataclass
class DownloadMusicResponse:
  play: str