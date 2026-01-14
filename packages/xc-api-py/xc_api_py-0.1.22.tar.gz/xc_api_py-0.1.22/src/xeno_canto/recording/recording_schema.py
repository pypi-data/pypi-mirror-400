from xeno_canto.recording.recording_fields import (
  CatalogueNumberField,
  RecordistField,
  QualityField,
  RemarksField,
  LengthField,
  UploadDateField,
  DeviceField,
  MicrophoneField,
  SampleRateField,
  PlaybackField,
  MethodField,
  AutomaticField,
  RecordedDateField,
  RecordedTimeField,
  SonogramsField,
  OscillogramsField,
  LicenseUrlField,
  XcPageField,
  FileDownloadField,
  FileNameField,
  GroupField,
  GenusField,
  EpithetField,
  SubspeciesField,
  CommonNameField,
  SoundTypeField,
  SexField,
  LifeStageField,
  BackgroundField,
  SeenField,
  RegistrationField,
  CountryField,
  LocalityField,
  LatitudeField,
  LongitudeField,
  AltitudeField,
  TempField,
)
from xeno_canto.patterns import license_pattern


from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional


class XenoCantoRecordingLeanSchema(BaseModel):
  model_config = ConfigDict(
    arbitrary_types_allowed=True,
    populate_by_name=True,  # Essential for XC API tag mapping
  )
  number: CatalogueNumberField
  genus: GenusField
  epithet: EpithetField
  common_name: CommonNameField
  recordist: RecordistField
  country: CountryField
  file_name: FileNameField
  file_download: FileDownloadField
  page: XcPageField
  license_url: LicenseUrlField
  upload_date: UploadDateField
  length: LengthField
  quality: QualityField

  sonograms: SonogramsField
  oscillograms: OscillogramsField

  @computed_field
  def id(self) -> int:
    if self.number:
      return self.number
    raise ValueError()

  @computed_field
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


class XenoCantoRecordingSchema(XenoCantoRecordingLeanSchema):
  date: RecordedDateField
  group: GroupField
  subspecies: SubspeciesField
  locality: LocalityField
  sound_type: SoundTypeField
  sex: SexField
  life_stage: LifeStageField
  seen: SeenField
  playback: PlaybackField
  background: BackgroundField
  latitude: LatitudeField
  longitude: LongitudeField
  altitude: AltitudeField
  temp: TempField
  method: MethodField
  time: RecordedTimeField
  remarks: RemarksField
  registration: RegistrationField
  automatic: AutomaticField
  device: DeviceField
  microphone: MicrophoneField
  sample_rate: SampleRateField
