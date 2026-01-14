from typing import Literal
from enum import IntEnum, auto
from typing import (
  Union,
)


class QualityRating(IntEnum):
  A = auto()
  B = auto()
  C = auto()
  D = auto()
  E = auto()

  @classmethod
  def max(cls) -> 'QualityRating':
    return QualityRating(min(c.value for c in cls))

  @classmethod
  def min(cls) -> 'QualityRating':
    return QualityRating(max(c.value for c in cls))

  def __add__(self, other):
    if isinstance(other, int):
      new_value = max(self.value - other, self.max())
      return QualityRating(new_value)
    return NotImplemented

  def __sub__(self, other):
    if isinstance(other, int):
      new_value = min(self.value + other, self.min())
      return QualityRating(new_value)
    return NotImplemented


Area = Literal[
  'africa',
  'america',
  'asia',
  'australia',
  'europe',
]

Sex = Literal[
  'male',
  'female',
]

LifeStage = Literal[
  'adult',
  'juvenile',
  'nestling',
  'nymph',
  'subadult',
]

RecordingMethod = Literal[
  'emerging from roost',
  'field recording',
  'fluorescent light tag',
  'hand-release',
  'in enclosure',
  'in net',
  'in the hand',
  'roosting',
  'roped',
  'studio recording',
]

Group = Literal[
  'grasshoppers',
  'bats',
  'birds',
  'frogs',
  'land mammals',
]

SoundType = Literal[
  'aberrant',
  'advertisement call',
  'agonistic call',
  'alarm call',
  'begging call',
  'call',
  'calling song',
  'courtship song',
  'dawn song',
  'defensive call',
  'distress call',
  'disturbance song',
  'drumming',
  'duet',
  'echolocation',
  'feeding buzz',
  'female song',
  'flight call',
  'flight song',
  'imitation',
  'mating call',
  'mechanical sound',
  'nocturnal flight call',
  'release call',
  'rivalry song',
  'searching song',
  'social call',
  'song',
  'subsong',
  'territorial call',
]


RecordingId = Union[str, int]
