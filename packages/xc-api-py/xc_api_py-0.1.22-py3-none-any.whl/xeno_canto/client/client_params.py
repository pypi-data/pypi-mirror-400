from xeno_canto.query.query_params import XenoCantoQueryParams
from xeno_canto.client.client_types import ReturnMode

from typing import (
  TypedDict,
)


class SearchQueryParams(
  XenoCantoQueryParams,
  TypedDict,
  total=False,
):
  mode: ReturnMode
  limit: int
  lean: bool
  stream: bool
