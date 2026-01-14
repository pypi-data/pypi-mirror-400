from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import (
  LimiterSession,
  LimiterMixin,
  SQLiteBucket,
)
from typing import Optional
from datetime import timedelta


class CachedLimiterSession(CacheMixin, LimiterMixin, Session): ...


def get_session(user_agent: Optional[str] = None, **kwargs):
  s = Session(**kwargs)
  if user_agent:
    s.headers.update({'User-Agent': user_agent})
  return s


def get_limiter_session(
  user_agent: Optional[str] = None,
  **kwargs,
):
  s = LimiterSession(
    **kwargs,
  )
  if user_agent:
    s.headers.update({'User-Agent': user_agent})
  return s


def get_cached_limiter_session(
  user_agent: Optional[str] = None,
  ttl: Optional[timedelta] = None,
  **kwargs,
):
  s = CachedLimiterSession(
    **kwargs,
    allowable_codes=[200],
    expire_after=ttl,
    bucket_class=SQLiteBucket,
    bucket_kwargs=dict(
      path=kwargs.get('bucket_cache_name', kwargs.get('cache_name', None)),
      isolation_level='EXCLUSIVE',
      check_same_thread=False,
    ),
  )
  if user_agent:
    s.headers.update({'User-Agent': user_agent})
  return s
