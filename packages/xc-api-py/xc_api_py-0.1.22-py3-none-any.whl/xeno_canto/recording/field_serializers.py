from xeno_canto.types import QualityRating

import yarl
import datetime


def serialize_url(v):
  if isinstance(v, yarl.URL):
    return str(v)
  return v


def serialize_quality_rating(v):
  if isinstance(v, QualityRating):
    return v.name
  return v


def serialize_datetime_date(v):
  if isinstance(v, datetime.date):
    return v.isoformat()
  return v
