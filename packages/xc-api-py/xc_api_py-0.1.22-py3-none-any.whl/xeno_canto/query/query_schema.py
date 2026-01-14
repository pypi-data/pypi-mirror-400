from xeno_canto.query import query_fields as F

from pydantic import BaseModel, ConfigDict
from typing import Optional


class XenoCantoQuerySchema(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True, serialize_by_alias=True)

  genus: F.GenusField
  epithet: F.EpithetField
  subspecies: F.SubspeciesField
  group: F.GroupField
  recordist: F.RecordistField
  country: F.CountryField
  location: F.LocalityField
  remarks: F.RemarksField
  seen: F.SeenField
  playback: F.PlaybackField
  background: F.BackgroundField
  sound_type: F.SoundTypeField
  sex: F.SexField
  life_stage: F.LifeStageField
  method: F.MethodField
  xc_number: F.IdField
  license: F.LicenseField
  quality: F.QualityField
  length: F.LengthField
  area: F.AreaField
  since: F.SinceField
  year: Optional[int] = None
  month: Optional[int] = None
  colyear: Optional[int] = None
  colmonth: Optional[int] = None
  registration: F.RegistrationField
  automatic: F.AutomaticField
  device: F.DeviceField
  microphone: F.MicrophoneField
  sample_rate: F.SampleRateField
  box: F.BoxField
