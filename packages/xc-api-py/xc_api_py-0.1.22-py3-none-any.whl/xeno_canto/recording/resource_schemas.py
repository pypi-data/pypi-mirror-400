from xeno_canto.recording.common_fields import UrlField

from pydantic import (
  BaseModel,
  ConfigDict,
  Field,
)


class OscillogramsSchema(BaseModel):
  model_config = ConfigDict(
    arbitrary_types_allowed=True,
  )

  small: UrlField = Field(default=None)
  medium: UrlField = Field(default=None, validation_alias='med')
  large: UrlField = Field(default=None)


class SonogramsSchema(BaseModel):
  model_config = ConfigDict(
    arbitrary_types_allowed=True,
  )

  small: UrlField = Field(default=None)
  medium: UrlField = Field(default=None, validation_alias='med')
  large: UrlField = Field(default=None)
  full: UrlField = Field(default=None)
