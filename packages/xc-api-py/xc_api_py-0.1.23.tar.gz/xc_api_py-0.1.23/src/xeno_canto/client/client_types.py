from __future__ import annotations
from typing import (
  Literal,
  Union,
  Dict,
  Any,
  TypeAlias,
)

ReturnMode: TypeAlias = Literal[
  'dataclass',
  'dict',
]

XenoCantoRecord: TypeAlias = Union[
  'XenoCantoRecordingLeanSchema',  # noqa: F821 # type: ignore
  'XenoCantoRecordingSchema',  # noqa: F821 # type: ignore
  'XenoCantoRecording',  # noqa: F821 # type: ignore
  'XenoCantoRecordingLean',  # noqa: F821 # type: ignore
]

AnyRecord: TypeAlias = Union[
  XenoCantoRecord,
  Dict[str, Any],
  str,  # JSON
]

Query: TypeAlias = Union[
  Dict[str, Any],
  'XenoCantoQuerySchema',  # noqa: F821 # type: ignore
]
