from xeno_canto.tags import tags
from xeno_canto.types import QualityRating
from typing import Union

import datetime
from datetime import timedelta


def serialize_numeric_tag(v):
  if isinstance(v, tags.NumericTag):
    match v.constraint:
      case 'at least':
        return f'">{v.a}"'
      case 'at most':
        return f'"<{v.a}"'
      case 'exactly':
        return f'"={v.a}"'
      case 'between':
        return f'"{v.a}-{v.b}"'
      case _:
        return f'{v.a}'

  return v


def serialize_boolean(v):
  if isinstance(v, bool):
    return 'yes' if v else 'no'
  return v


def serialize_datetime_date(v):
  if isinstance(v, datetime.date):
    return v.isoformat()
  return v


# LengthTag, datetime.timedelta, float, int
def serialize_datetime_timedelta_as_seconds(v: Union[tags.LengthTag, timedelta, float, int]):
  if isinstance(v, tags.LengthTag):
    a = v.a
    if isinstance(a, timedelta):
      a = a.total_seconds()
    b = v.b

    match (v.constraint, a, b):
      case ('at least', a, _):
        return f'">{int(a)}'
      case ('at most', a, _):
        return f'"<{int(a)}'
      case ('between', a, b):
        if b is None:
          raise ValueError()
        elif isinstance(b, timedelta):
          b = b.total_seconds()
        return f'{int(a)}-{int(b)}'
      case ('exactly', a, _):
        return f'"={a}"'
      case (_, a, _):
        return str(int(a))

  elif isinstance(v, datetime.timedelta):
    return str(int(v.total_seconds()))

  return str(int(v))


MAX_Q = QualityRating.max()
MIN_Q = QualityRating.min()


def serialize_quality_rating(v):
  if isinstance(v, str):
    return v

  elif isinstance(v, QualityRating):
    return v.name

  elif isinstance(v, int):
    return QualityRating(v).name

  elif isinstance(v, tags.QualityTag):
    match (v.constraint, v.a):
      case ('at most', r) if r == QualityRating.max():
        # NOTE Allow all qualities
        return None
      case ('at most', r) if r == QualityRating.min():
        return r.name
      case ('at most', r):
        return f'"<{(r + 1).name}"'

      case ('at least', r) if r == QualityRating.max():
        return r.name
      case ('at least', r) if r == QualityRating.min():
        # NOTE Allow all qualities
        return None
      case ('at least', r):
        return f'">{(r - 1).name}"'

      case (_, r):
        return r.name

  raise ValueError(v)


def serialize_country(v):
  if isinstance(v, tags.CountryTag):
    v = v.name

  elif isinstance(v, str):
    if ' ' in v and not (v.startswith('"') and v.endswith('"')):
      v = f'"{v}"'
    v = v

  return v


def serialize_box(v):
  if isinstance(v, tags.BoxTag):
    return f'{v.ay},{v.ax},{v.by},{v.bx}'

  elif isinstance(v, tuple):
    ay, ax, by, bx = v
    return f'{ay},{ax},{by},{bx}'

  return v
