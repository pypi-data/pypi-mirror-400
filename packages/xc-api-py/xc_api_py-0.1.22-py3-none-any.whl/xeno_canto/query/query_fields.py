from xeno_canto.tags import tags
from xeno_canto import types as T
from xeno_canto.constants import aliases
from xeno_canto.query import field_serializers as fs

from typing import (
  Annotated,
  Optional,
  Union,
  List,
  Tuple,
)
from pydantic import (
  Field,
  PlainSerializer,
)
import datetime


SexField = Annotated[
  Optional[T.Sex],
  Field(
    default=None,
    title='Sex of the recorded animal',
    serialization_alias=aliases.SEX,
  ),
]

LifeStageField = Annotated[
  Optional[Union[T.LifeStage, List[T.LifeStage]]],
  Field(
    default=None,
    title='Life stage of the recorded animal',
    serialization_alias=aliases.LIFE_STAGE,
  ),
]

SoundTypeField = Annotated[
  Optional[T.SoundType],
  Field(
    default=None,
    title='Call type of the recorded animal',
    serialization_alias=aliases.SOUND_TYPE,
  ),
]

BackgroundField = Annotated[
  Optional[List[str]],
  Field(
    default=None,
    title='Background species identified in the recording',
    serialization_alias=aliases.BACKGROUND_SPECIES,
    examples=[['Turdus viscivorus', 'Parus major']],
  ),
]

RegistrationField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Registration number (if specimen collected)',
    serialization_alias=aliases.REG_NUMBER,
  ),
]

SeenField = Annotated[
  Optional[bool],
  Field(
    default=None,
    title='Recorded animal was seen by the recordist',
    serialization_alias=aliases.ANIMAL_SEEN,
  ),
]

GenusField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Generic name of the species',
    serialization_alias=aliases.GENUS,
    description="""
    Genus is part of a species' scientific name, so it is searched by default when performing a basic search.
    But you can use the gen tag to limit your search query only to the genus field.
    These fields use a 'starts with' query and accept a 'matches' operator.
    """,
    examples=['[halcyon] smyrnensis smyrnensis'],
  ),
]

EpithetField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Specific name (epithet) of the species',
    serialization_alias=aliases.EPITHET,
    examples=['halcyon [smyrnensis] smyrnensis'],
  ),
]

SubspeciesField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Subspecies epithet.',
    serialization_alias=aliases.SUBSPECIES,
    examples=['halcyon smyrnensis [smyrnensis]'],
  ),
]

GroupField = Annotated[
  Optional[T.Group],
  Field(
    default=None,
    title='Group to which the species belongs.',
    serialization_alias=aliases.GROUP,
    description="""
    Use the grp tag to narrow down your search to a specific group.
    Valid group values are birds, grasshoppers, bats, frogs and land mammals.
    You can also use their respective ids (1 to 5).
    """,
  ),
]

CountryField = Annotated[
  Optional[Union[tags.CountryTag, str]],
  Field(
    default=None,
    title='Country where the recording was made',
    serialization_alias=aliases.COUNTRY,
    examples=['Spain'],
  ),
  PlainSerializer(fs.serialize_country),
]

LocalityField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Locality where the recording was made',
    serialization_alias=aliases.LOCALITY,
    examples=['Sisalde, Ames, A Coruña, Galicia'],
  ),
]

# Deprecated; Use BoxField instead
LatitudeField = Annotated[
  Optional[float],
  Field(
    default=None,
    title='Latitude of the recording location (degrees)',
    serialization_alias=aliases.LATITUDE,
  ),
]

# Deprecated; Use BoxField instead
LongitudeField = Annotated[
  Optional[float],
  Field(
    default=None,
    title='Longitude of the recording location (degrees)',
    serialization_alias=aliases.LONGITUDE,
  ),
]

# Deprecated
TempField = Annotated[
  Optional[float],
  Field(
    default=None,
    title='Temperature during recording (celsius)',
    serialization_alias=aliases.TEMP,
  ),
]

AreaField = Annotated[
  Optional[T.Area],
  Field(
    default=None,
    description='The area tag allows you to search by world area. Valid values for this tag are africa, america, asia, australia, europe.',
    serialization_alias=aliases.AREA,
  ),
]

IdField = Annotated[
  Optional[Union[int]],
  Field(
    default=None,
    title='Catalogue number of the recording on Xeno Canto',
    description="""
    All recordings on xeno-canto are assigned a unique catalog number (generally displayed in the form XC76967).
    To search for a known recording number, use the nr tag: for example nr:76967.
    You can also search for a range of numbers as nr:88888-88890.
    """,
    serialization_alias=aliases.XC_NUMBER,
    examples=[694038],
  ),
]

MicrophoneField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Microphone device model that used to record',
    serialization_alias=aliases.MICROPHONE,
  ),
]

DeviceField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Recording device model used',
    serialization_alias=aliases.DEVICE,
  ),
]

SampleRateField = Annotated[
  Optional[Union[tags.SampleRateTag, int]],
  Field(
    default=None,
    title='Sample rate of the recording',
    serialization_alias=aliases.SAMPLE_RATE,
  ),
  PlainSerializer(fs.serialize_numeric_tag),
]

RecordistField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Name of the recordist',
    description=r"To search for all recordings from a particular recordist, use the rec tag. For example, rec:John will return all recordings from recordists whose names contain the string \"John\". This field accepts a 'matches' operator.",
    serialization_alias=aliases.RECORDIST,
    examples=['Jacobo Ramil Millarengo'],
  ),
]

RemarksField = Annotated[
  Optional[str],
  Field(
    default=None,
    title='Additional remarks made by the recordist',
    serialization_alias=aliases.REMARKS,
    examples=['Male repeating a stereotyped phrase. HPF 270 Hz.'],
  ),
]

LengthField = Annotated[
  Optional[Union[tags.LengthTag, datetime.timedelta, float, int]],
  Field(
    default=None,
    title='Length of the recording (minutes, seconds)',
    serialization_alias=aliases.LENGTH,
    examples=['4:08'],
  ),
  PlainSerializer(fs.serialize_datetime_timedelta_as_seconds),
]

QualityField = Annotated[
  Optional[Union[tags.QualityTag, T.QualityRating, str]],
  Field(
    default=None,
    title='Recording quality rating',
    serialization_alias=aliases.XC_QUALITY,
  ),
  PlainSerializer(fs.serialize_quality_rating),
]


PlaybackField = Annotated[
  Optional[bool],
  Field(
    default=None,
    title='Playback was used to lure the animal.',
    serialization_alias=aliases.PLAYBACK_USED,
  ),
  PlainSerializer(fs.serialize_boolean),
]

AutomaticField = Annotated[
  Optional[bool],
  Field(
    default=None,
    title='Indicator for automatic/non-supervised recording',
    serialization_alias='auto',
  ),
  PlainSerializer(fs.serialize_boolean),
]

SinceField = Annotated[
  Optional[Union[tags.SinceTag, datetime.date, str, int]],
  Field(
    default=None,
    title='Upload date filter',
    description="""
    The since tag allows you to search for recordings that have been uploaded since a certain date. 
    Using a simple integer value such as since:3 will find all recordings uploaded in the past 3 days. 
    If you use a date with a format of YYYY-MM-DD, it will find all recordings uploaded since that date.
    Note that this search considers the upload date, not the date that the recording was made.
    """,
    serialization_alias=aliases.SINCE,
    examples=['2021-12-23'],
  ),
  PlainSerializer(fs.serialize_datetime_date),
]

MethodField = Annotated[
  Optional[T.RecordingMethod],
  Field(
    default=None,
    title='Method of the recording',
    serialization_alias=aliases.RECORDING_METHOD,
  ),
]

LicenseField = Annotated[
  Optional[str],
  Field(
    default=None,
    description="""
    Recordings on xeno-canto are licensed under a small number of different Creative Commons licenses.
    You can search for recordings that match specific license conditions using the lic tag.
    License conditions are Attribution (BY), NonCommercial (NC), ShareAlike (SA), NoDerivatives (ND) and Public Domain/copyright free (CC0).
    Conditions should be separated by a '-' character.
    For instance, to find recordings that are licensed under an Attribution-NonCommercial-ShareAlike license, use lic:BY-NC-SA;
    for "no rights reserved" recordings, use lic:PD.
    See the Creative Commons website for more details about the individual licenses.
    """,
    serialization_alias=aliases.LICENSE,
  ),
]

BoxField = Annotated[
  Optional[Union[tags.BoxTag, Tuple[float, float, float, float]]],
  Field(
    default=None,
    description="""
    The second tag allows you to search for recordings that occur within a given rectangle, and is called box.
    It is more versatile than lat and lon, but is more awkward to type in manually, so we have made a map-based search tool to make things simpler.
    The general format of the box tag is as follows: box:LAT_MIN,LON_MIN,LAT_MAX,LON_MAX.
    Note that there must not be any spaces between the coordinates.
    """,
    serialization_alias=aliases.BOX,
  ),
  PlainSerializer(fs.serialize_box),
]
