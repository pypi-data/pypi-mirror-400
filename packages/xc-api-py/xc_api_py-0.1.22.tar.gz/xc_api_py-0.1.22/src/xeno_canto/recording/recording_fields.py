from xeno_canto.recording.field_validators import (
  get_validator,
  validate_url,
  validate_boolean,
  validate_string,
  validate_dt_timedelta,
  validate_dt_date,
  validate_dt_time,
  validate_xc_quality,
  validate_integer,
  validate_xc_number,
  validate_float,
  validate_literal,
  validate_literal_list,
  validate_string_list,
)
from xeno_canto.recording.field_serializers import (
  serialize_url,
)
from xeno_canto.types import (
  QualityRating,
  Sex,
  LifeStage,
  SoundType,
  RecordingMethod,
  Group,
)
from xeno_canto.constants import aliases
from xeno_canto.recording.resource_schemas import (
  SonogramsSchema,
  OscillogramsSchema,
)


import yarl
import datetime
from typing import (
  Annotated,
  Optional,
  List,
)
from pydantic import (
  BeforeValidator,
  PlainSerializer,
  Field,
)

CatalogueNumberField = Annotated[
  int,  # Made non-optional as it's the primary key
  BeforeValidator(get_validator(validate_xc_number, allow_none=False)),
  Field(
    title='Catalogue number of the recording on Xeno Canto',
    validation_alias=aliases.XC_ID,
    examples=[694038],
  ),
]

MicrophoneField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='Microphone device model that used to record',
    validation_alias=aliases.MICROPHONE,
  ),
]

DeviceField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='Recording device model used',
    validation_alias=aliases.DEVICE,
  ),
]

RecordistField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='Name of the recordist',
    validation_alias=aliases.RECORDIST,
    examples=['Jacobo Ramil Millarengo'],
  ),
]

RemarksField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='Additional remarks made by the recordist',
    validation_alias=aliases.REMARKS,
    examples=['Male repeating a stereotyped phrase. HPF 270 Hz.'],
  ),
]


UploadDateField = Annotated[
  Optional[datetime.date],
  BeforeValidator(get_validator(validate_dt_date, allow_none=True)),
  Field(
    default=None,
    title='Date the recording was uploaded to Xeno Canto',
    validation_alias=aliases.UPLOAD_DATE,
    examples=['2021-12-27'],
  ),
]

SampleRateField = Annotated[
  Optional[int],
  BeforeValidator(get_validator(validate_integer, allow_none=True)),
  Field(
    default=None,
    title='Sample rate of the recording',
    validation_alias=aliases.SAMPLE_RATE,
  ),
]

LengthField = Annotated[
  Optional[datetime.timedelta],
  BeforeValidator(get_validator(validate_dt_timedelta, allow_none=True)),
  Field(
    default=None,
    title='Length of the recording (minutes, seconds)',
    validation_alias=aliases.LENGTH,
    examples=['4:08'],
  ),
]

QualityField = Annotated[
  Optional[QualityRating],
  BeforeValidator(get_validator(validate_xc_quality, allow_none=True)),
  Field(
    default=None,
    title='Recording quality rating',
    validation_alias=aliases.XC_QUALITY,
  ),
]


PlaybackField = Annotated[
  Optional[bool],
  BeforeValidator(get_validator(validate_boolean, allow_none=True)),
  Field(
    title='Playback was used to lure the animal.',
    validation_alias=aliases.PLAYBACK_USED,
  ),
]

AutomaticField = Annotated[
  Optional[bool],
  BeforeValidator(get_validator(validate_boolean, allow_none=True)),
  Field(
    title='Indicator for automatic/non-supervised recording',
    validation_alias=aliases.AUTOMATIC,
  ),
]

RecordedDateField = Annotated[
  Optional[datetime.date],
  BeforeValidator(get_validator(validate_dt_date, allow_none=True)),
  Field(
    title='Date the recording was made',
    validation_alias=aliases.RECORDED_DATE,
    examples=['2021-12-23'],
  ),
]

RecordedTimeField = Annotated[
  Optional[datetime.time],
  BeforeValidator(get_validator(validate_dt_time, allow_none=True)),
  Field(
    title='Time of day when the recording was made',
    validation_alias=aliases.RECORDED_TIME,
    examples=['09:30'],
  ),
]

MethodField = Annotated[
  Optional[RecordingMethod],
  BeforeValidator(get_validator(validate_literal(RecordingMethod), allow_none=True)),
  Field(
    title='Method of the recording',
    validation_alias=aliases.RECORDING_METHOD,
  ),
]


SonogramsField = Annotated[
  Optional[SonogramsSchema],
  Field(
    default=None,
    title='URLs of the recording sonograms',
    validation_alias='sono',
  ),
]

OscillogramsField = Annotated[
  Optional[OscillogramsSchema],
  Field(
    default=None,
    title='URLs of the recording oscillograms',
    validation_alias='osci',
  ),
]
LicenseUrlField = Annotated[
  Optional[yarl.URL],
  BeforeValidator(get_validator(validate_url, allow_none=True)),
  Field(
    default=None,
    title='URL describing the license of this recording',
    validation_alias=aliases.LICENSE,
  ),
  PlainSerializer(serialize_url, return_type=str),
]

XcPageField = Annotated[
  Optional[yarl.URL],
  BeforeValidator(get_validator(validate_url, allow_none=True)),
  Field(
    default=None,
    title='URL specifying the details of this recording',
    validation_alias=aliases.PAGE_URL,
  ),
  PlainSerializer(serialize_url, return_type=str),
]

FileDownloadField = Annotated[
  Optional[yarl.URL],
  BeforeValidator(get_validator(validate_url, allow_none=True)),
  Field(
    default=None,
    title='(base) URL to the audio file',
    validation_alias=aliases.FILE,
  ),
  PlainSerializer(serialize_url, return_type=str),
]

FileNameField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='Original file name of the audio file',
    validation_alias=aliases.FILE_NAME,
  ),
]


CountryField = Annotated[
  str,
  BeforeValidator(get_validator(validate_string)),
  Field(
    default=None,
    title='Country where the recording was made',
    validation_alias=aliases.COUNTRY,
    examples=['Spain'],
  ),
]

LocalityField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='Locality where the recording was made',
    validation_alias=aliases.LOCALITY,
    examples=['Sisalde, Ames, A Coruña, Galicia'],
  ),
]

LatitudeField = Annotated[
  Optional[float],
  BeforeValidator(get_validator(validate_float, allow_none=True)),
  Field(
    default=None,
    title='Latitude of the recording location (degrees)',
    validation_alias=aliases.LATITUDE,
  ),
]

LongitudeField = Annotated[
  Optional[float],
  BeforeValidator(get_validator(validate_float, allow_none=True)),
  Field(
    default=None,
    title='Longitude of the recording location (degrees)',
    validation_alias=aliases.LONGITUDE,
  ),
]

AltitudeField = Annotated[
  Optional[float],
  BeforeValidator(get_validator(validate_float, allow_none=True)),
  Field(
    default=None,
    title='Altitude of the recording location (meters)',
    validation_alias=aliases.ALTITUDE,
  ),
]

TempField = Annotated[
  Optional[float],
  BeforeValidator(get_validator(validate_float, allow_none=True)),
  Field(
    default=None,
    title='Temperature during recording (celsius)',
    validation_alias=aliases.TEMP,
  ),
]


SexField = Annotated[
  List[Sex],
  BeforeValidator(get_validator(validate_literal_list(Sex), allow_none=True, default_factory=list)),
  Field(
    default=None,
    title='Sex of the recorded animal',
    validation_alias=aliases.SEX,
  ),
]

LifeStageField = Annotated[
  List[LifeStage],
  BeforeValidator(get_validator(validate_literal_list(LifeStage), default_factory=list)),
  Field(
    default_factory=list,
    title='Life stage of the recorded animal',
    validation_alias=aliases.LIFE_STAGE,
  ),
]

SoundTypeField = Annotated[
  List[SoundType],
  BeforeValidator(get_validator(validate_literal_list(SoundType), default_factory=list)),
  Field(
    default_factory=list,
    title='Call type of the recorded animal',
    validation_alias=aliases.SOUND_TYPE,
  ),
]

BackgroundField = Annotated[
  List[str],
  BeforeValidator(get_validator(validate_string_list, default_factory=list)),
  Field(
    default_factory=list,
    title='Background species identified in the recording',
    validation_alias=aliases.BACKGROUND_SPECIES,
    examples=[['Turdus viscivorus', 'Parus major']],
  ),
]

RegistrationField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    validation_alias=aliases.REG_NUMBER,
    description='Registration number (if specimen collected)',
  ),
]

SeenField = Annotated[
  Optional[bool],
  BeforeValidator(get_validator(validate_boolean, allow_none=True)),
  Field(
    default=None,
    description='Recorded animal was seen by the recordist',
    validation_alias=aliases.ANIMAL_SEEN,
  ),
]


GenusField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    validation_alias=aliases.GENUS,
    description='Generic name of the species',
    examples=['Halcyon'],
  ),
]

EpithetField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    validation_alias=aliases.EPITHET,
    description='Specific name (epithet) of the species',
    examples=['smyrnensis'],
  ),
]

SubspeciesField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    validation_alias=aliases.SUBSPECIES,
    description='Subspecies epithet.',
    examples=['smyrnensis'],
  ),
]

GroupField = Annotated[
  Optional[Group],
  BeforeValidator(get_validator(validate_literal(Group), allow_none=True)),
  Field(
    default=None,
    validation_alias=aliases.GROUP,
    description='Group to which the species belongs.',
  ),
]

CommonNameField = Annotated[
  Optional[str],
  BeforeValidator(get_validator(validate_string, allow_none=True)),
  Field(
    default=None,
    title='English name of the species',
    validation_alias=aliases.COMMON_NAME,
    examples=['White-throated Kingfisher'],
  ),
]
