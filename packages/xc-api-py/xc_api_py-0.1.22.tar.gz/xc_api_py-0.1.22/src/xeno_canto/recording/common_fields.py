from xeno_canto.recording.field_validators import (
  validate_url,
)
from xeno_canto.recording.field_serializers import (
  serialize_url,
)


import yarl
from typing import (
  Annotated,
  Optional,
)
from pydantic import (
  BeforeValidator,
  PlainSerializer,
)

UrlField = Annotated[
  Optional[yarl.URL],
  BeforeValidator(validate_url),
  PlainSerializer(serialize_url, return_type=str),
]
