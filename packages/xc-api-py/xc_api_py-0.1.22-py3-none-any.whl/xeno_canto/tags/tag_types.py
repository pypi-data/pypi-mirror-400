from typing import (
  Literal,
  Union,
  Tuple,
)

import datetime

Contraint = Literal[
  'exactly',
  'at least',
  'at most',
  'between',
]

Area = Literal[
  'africa',
  'america',
  'asia',
  'australia',
  'europe',
]

Numeric = Union[float, int, datetime.timedelta]
