from xeno_canto.types import QualityRating
from xeno_canto.patterns import float_pattern, partial_date_pattern

from functools import wraps
from typing import (
  Any,
  get_args,
  Callable,
  Sequence,
  List,
)
import yarl
import pathlib
import dateutil.parser as dtparser
import datetime

INVALID_STRING_INPUTS = [
  '',
  '?',
  'unknown',
  'no score',
  'uncertain',
  'not specified',
  'xx:xx',
  '??:??',
  '?:?',
]


def get_validator(
  func: Callable,
  allow_none: bool = True,
  default_factory: Callable = lambda: None,
) -> Callable:
  @wraps(func)
  def wrapper(v: Any, *args, **kwargs) -> Any:
    # 1. Handle explicit None
    if v is None:
      return default_factory()

    # 2. Handle Dirty Strings
    if isinstance(v, str):
      v_clean = v.strip()
      if v_clean.lower() in INVALID_STRING_INPUTS:
        return default_factory()  # Use factory instead of None
      v = v_clean

    # 3. Core Validation
    try:
      return func(v, *args, **kwargs)
    except (ValueError, TypeError, KeyError, AttributeError):
      if not allow_none:  # If NOT allowing none/defaults, raise the error
        raise
      return default_factory()  # Otherwise return the safe default (e.g., [])

  return wrapper


def validate_literal(literal_type):
  allowed = {str(a).lower() for a in get_args(literal_type)}

  def validator(v):
    if str(v).lower() in allowed:
      return v
    raise ValueError(v)

  return validator


def validate_literal_list(literal_type):
  allowed = set(get_args(literal_type))

  def validator(v: Any) -> List[str]:
    # 1. Handle None/Empty
    if not v:
      return []

    # 2. Normalize input to a collection of parts
    if isinstance(v, str):
      # Split 'male, female' into ['male', 'female']
      parts = v.split(',')
    elif isinstance(v, list):
      parts = v
    else:
      return []

    # 3. Filter and clean
    cleaned = []
    for p in parts:
      s = str(p).strip().lower()
      if s in allowed:
        cleaned.append(s)

    # 4. ALWAYS return a list, satisfying List[Sex]
    return cleaned

  return validator


def validate_string(v):
  if isinstance(v, str):
    return v

  raise ValueError(v)


def validate_string_list(v):
  if not v:
    return []

  if isinstance(v, str):
    v = [v]

  if isinstance(v, Sequence):
    processed = [validate_string(u) for u in v]
    result = [u for u in processed if u is not None]

    if not result:
      raise ValueError('No valid strings in list')

    return result

  raise ValueError(f'Expected sequence, got {type(v)}')


def validate_url(v):
  if isinstance(v, yarl.URL):
    return v
  if isinstance(v, str):
    # Only prepend if it's a protocol-relative URL
    url_str = f'https:{v}' if v.startswith('//') else v
    return yarl.URL(url_str)
  return None


def validate_pathlib_path(v):
  if v is None:
    return None

  if isinstance(v, pathlib.Path):
    return v

  if isinstance(v, str):
    return pathlib.Path(v)

  raise ValueError(v)


def validate_float(v):
  if isinstance(v, float):
    return v

  if isinstance(v, str):
    match = float_pattern.match(v)
    if match:
      return float(match.group(1))

  raise ValueError(v)


def validate_dt_date(v):
  if isinstance(v, datetime.date):
    return v

  if isinstance(v, str):
    # 1. Handle the '00' day edge case
    if match := partial_date_pattern.match(v):
      year = int(match.group('year'))
      month = int(match.group('month'))

      # If month is also '00', default to January
      clean_month = max(1, month)
      return datetime.date(year, clean_month, 1)

    # 2. Fallback to standard ISO parsing for valid strings
    return datetime.date.fromisoformat(v)

  raise ValueError(v)


def validate_dt_time(v):
  if isinstance(v, datetime.time):
    return v

  elif isinstance(v, str):
    return dtparser.parse(v).time()

  raise ValueError(v)


def validate_dt_timedelta(v):
  if isinstance(v, datetime.timedelta):
    return v

  elif isinstance(v, str):
    try:
      mm, ss = map(int, v.split(':'))
      return datetime.timedelta(minutes=mm, seconds=ss)

    except (ValueError, IndexError):
      raise ValueError(v) from None

  raise ValueError(v)


def validate_boolean(v):
  if isinstance(v, bool):
    return v

  if isinstance(v, str):
    if v.lower().startswith('yes'):
      return True
    elif v.lower().startswith('no'):
      return False

  raise ValueError(v)


def validate_xc_number(v):
  if isinstance(v, int):
    return v

  if isinstance(v, str):
    u = v.lower()
    if u.startswith('xc'):
      u = u.strip('xc')
    return int(u)

  raise ValueError(v)


def validate_xc_quality(v):
  if isinstance(v, QualityRating):
    return v

  if isinstance(v, str):
    return QualityRating[v.capitalize()]

  raise ValueError(v)


def validate_integer(v):
  if isinstance(v, int):
    return v

  if isinstance(v, str):
    return int(v)

  raise ValueError(v)
