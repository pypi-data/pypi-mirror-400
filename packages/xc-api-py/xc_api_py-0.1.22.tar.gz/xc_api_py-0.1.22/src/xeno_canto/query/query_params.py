from xeno_canto import types as T
from xeno_canto.tags import tags

from typing import TypedDict, Union, List, Tuple
import datetime


class XenoCantoQueryParams(TypedDict, total=False):
  box: Union[tags.BoxTag, Tuple[float, float, float, float]]
  genus: str
  epithet: str
  subspecies: str
  group: T.Group
  common_name: str
  recordist: str
  country: Union[tags.CountryTag, str]
  location: str
  remarks: str
  seen: bool
  playback: bool
  background: List[str]
  sound_type: T.SoundType
  sex: T.Sex
  life_stage: T.LifeStage
  method: T.RecordingMethod
  xc_number: int
  license: str  # FIXME
  quality: Union[tags.QualityTag, str]
  length: Union[tags.LengthTag, str]
  area: str
  since: Union[tags.SinceTag, str, int, datetime.timedelta]
  year: int
  month: int
  colyear: int
  colmonth: int
  registration: str
  automatic: bool
  device: str
  microphone: str
  sample_rate: Union[tags.SampleRateTag, int, str]
