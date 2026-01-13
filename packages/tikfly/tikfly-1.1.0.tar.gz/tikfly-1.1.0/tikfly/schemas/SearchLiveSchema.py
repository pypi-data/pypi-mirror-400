from typing import List
from dataclasses import dataclass

@dataclass
class RoomInfo:
  has_commerce_goods: bool
  is_battle: bool

@dataclass
class LiveInfo:
  raw_data: str
  room_info: RoomInfo

@dataclass
class LiveDataItem:
  live_info: LiveInfo

@dataclass
class LogPB:
  impr_id: str

@dataclass
class SearchLiveResponse:
  hasMore: int
  cursor: int
  log_pb: LogPB
  data: List[LiveDataItem]