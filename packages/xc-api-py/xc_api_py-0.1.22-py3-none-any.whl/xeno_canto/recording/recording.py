from xeno_canto.patterns import license_pattern
from xeno_canto.types import (
  SoundType,
  Sex,
  LifeStage,
  RecordingMethod,
)

from dataclasses import (
  dataclass,
  fields,
  field,
)
from typing import (
  Optional,
  List,
  Union,
)
from functools import cached_property
import yarl
import pydantic
import pathlib
import datetime


@dataclass(frozen=True)
class XenoCantoRecordingLean:
  number: int
  genus: str
  epithet: str
  common_name: str
  recordist: str
  country: str
  file_name: str
  file_download: yarl.URL
  page: yarl.URL
  license_url: yarl.URL
  upload_date: datetime.date
  length: datetime.timedelta
  quality: str

  sonograms: dict[str, yarl.URL]
  oscillograms: dict[str, yarl.URL]

  @classmethod
  def from_pydantic(cls, m: pydantic.BaseModel):
    class_fields = {f.name for f in fields(cls)}
    data = {k: v for k, v in m.model_dump(exclude_computed_fields=True).items() if k in class_fields}

    return cls(**data)

  @property
  def id(self) -> int:
    return self.number

  @cached_property
  def license(self) -> Optional[str]:
    if not self.license_url:
      return None

    match = license_pattern.search(str(self.license_url))
    if match:
      parts = match.groupdict()
      lic_name = parts['name']
      version = parts['ver']

      # Normalization: xeno-canto uses 'zero' in the URL for CC0
      if lic_name == 'zero':
        lic_name = 'cc0'

      return f'{lic_name},{version}'

    return None


@dataclass(frozen=True)
class XenoCantoRecording(XenoCantoRecordingLean):
  date: Optional[datetime.date] = field(default=None)
  group: Optional[str] = field(default=None)
  subspecies: Optional[str] = field(default=None)
  locality: Optional[str] = field(default=None)
  sound_type: List[SoundType] = field(default_factory=list)
  sex: Optional[Sex] = field(default=None)
  life_stage: List[LifeStage] = field(default_factory=list)
  seen: Optional[bool] = field(default=None)
  playback: Optional[bool] = field(default=None)
  background: List[str] = field(default_factory=list)
  latitude: Optional[float] = field(default=None)
  longitude: Optional[float] = field(default=None)
  altitude: Optional[float] = field(default=None)
  method: Optional[RecordingMethod] = field(default=None)
  time: Optional[datetime.time] = field(default=None)
  remarks: Optional[str] = field(default=None)
  temp: Optional[float] = field(default=None)
  registration: Optional[Union[int, str]] = field(default=None)  # Often contains strings in XC
  automatic: Optional[bool] = field(default=None)
  device: Optional[str] = field(default=None)
  microphone: Optional[str] = field(default=None)
  sample_rate: Optional[int] = field(default=None)
