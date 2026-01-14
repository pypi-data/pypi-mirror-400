from xeno_canto.recording.recording_schema import (
  XenoCantoRecordingSchema,
  XenoCantoRecordingLeanSchema,
)
from xeno_canto.recording.recording import (
  XenoCantoRecording,
  XenoCantoRecordingLean,
)
from xeno_canto.query.query_schema import (
  XenoCantoQuerySchema,
)
from xeno_canto.client.client_errors import (
  ClientError,
  ServerError,
)
from xeno_canto.client.client_schemas import (
  XenoCantoResponseSchema,
)
from xeno_canto.client.client_params import (
  SearchQueryParams,
)
from xeno_canto import types as T
from xeno_canto.client.client_types import (
  ReturnMode,
  XenoCantoRecord,
  AnyRecord,
  Query,
)
from xeno_canto.client.client_http import (
  get_session,
  get_cached_limiter_session,
)

from typing import (
  Optional,
  Iterator,
  Union,
  List,
  Any,
  Unpack,
  Tuple,
  Set,
  Iterable,
  Literal,
)
import warnings
import re
from os import cpu_count
import random
from pathlib import Path
from datetime import datetime
from pydantic import (
  SecretStr,
)
from datetime import timedelta


class Client:
  _XC_API_BASE_URL = 'https://xeno-canto.org/api/3'
  _XC_MIN_PAGE_SIZE = 50
  _XC_DEFAULT_PAGE_SIZE = 100
  _XC_MAX_PAGE_SIZE = 500
  _XC_ID_PATTERN = re.compile(r'(?i:xc)?(?P<id>\d+)')
  _XC_MAX_ID = 950000
  _LEAN_FIELDS = set(XenoCantoRecordingLeanSchema.model_fields.keys())
  _SEARCH_LIMIT = 10000
  _USER_AGENT = 'Xeno-Canto-Client-py/1.0'
  _CACHE_NAME = '.xeno_cento_cache'

  def __init__(
    self,
    api_key: Union[SecretStr, str],
    verbose: bool = False,
  ):
    self._api_key = api_key.get_secret_value() if isinstance(api_key, SecretStr) else api_key
    self._verbose = verbose
    self._download_session = get_session(user_agent=self._USER_AGENT)
    self._recording_session = get_cached_limiter_session(
      per_second=4,
      burst=10,
      ttl=timedelta(days=1),
      user_agent=self._USER_AGENT,
      cache_name=self._CACHE_NAME,
    )
    self._max_workers = min(4, cpu_count() or 1)

  def _prepare_url(self, query: Query):
    if isinstance(query, XenoCantoQuerySchema):
      query = query.model_dump(
        exclude_none=True,
        exclude_computed_fields=True,
      )

    query_string = '+'.join(f'{k}:{v}' for k, v in query.items())

    params = dict(
      key=self._api_key,
      per_page=self._XC_MAX_PAGE_SIZE,
      query=query_string,
    )

    params_string = '&'.join(f'{k}={v}' for k, v in params.items())

    return f'{self._XC_API_BASE_URL}/recordings?{params_string}'

  def _fetch_from_api(self, url: str, page: int) -> XenoCantoResponseSchema:
    if page < 1:
      raise ValueError(page)

    resp = self._recording_session.get(f'{url}&page={page}')

    match resp.status_code:
      case 401:
        body = resp.json()
        msg = body.get(
          'message',
          "Missing or invalid 'key' parameter. Visit https://xeno-canto.org/account to retrieve your API key.",
        )
        raise ClientError(msg) from None

      case 400:
        body = resp.json()
        msg = body.get(
          'message',
          'Xeno-canto API v3 only accepts queries using tags. Visit https://xeno-canto.org/explore/api for a complete list.',
        )
        raise ClientError(f'{msg} ({resp.url})') from None

      case 503:
        raise ServerError(
          'Server responded with 503, you probably hit the rate-limit: https://xeno-canto.org/explore/api'
        ) from None

    resp.raise_for_status()
    return XenoCantoResponseSchema.model_construct(**resp.json())

  def _search(self, query: Query, limit: Optional[int] = None) -> Iterator[XenoCantoRecordingSchema]:
    if limit is not None and not (1 <= limit <= self._SEARCH_LIMIT):
      raise ValueError(limit)

    # 1. Probe Page 1 (ResponseSchema now contains List[dict])
    url = self._prepare_url(query)
    probe = self._fetch_from_api(url, page=1)
    if not probe.recordings:
      return

    yielded_count = 0

    for raw_record in probe.recordings:
      try:
        yield XenoCantoRecordingSchema.model_validate(raw_record)
        yielded_count += 1
      except Exception as e:
        if self._verbose:
          print(f'Skipping malformed record on page 1: {e}')
        continue

      if limit and yielded_count >= limit:
        return

    # 3. Handle subsequent pages sequentially
    total_pages = probe.num_pages
    current_page = 2

    while current_page <= total_pages:
      resp = self._fetch_from_api(url, current_page)

      if not resp or not resp.recordings:
        break

      for raw_record in resp.recordings:
        try:
          yield XenoCantoRecordingSchema.model_validate(raw_record)
          yielded_count += 1
        except Exception as e:
          if self._verbose:
            print(f'Skipping malformed record on page {current_page}: {e}')
          continue

        if limit and yielded_count >= limit:
          return

      current_page += 1

  @classmethod
  def _sanitize_rid(cls, rid: T.RecordingId) -> int:
    if isinstance(rid, str):
      rid = re.sub(r'^xc', '', rid.strip(), flags=re.IGNORECASE)

    clean_int = int(rid)

    if not 0 < clean_int < cls._XC_MAX_ID:
      raise ValueError(rid)

    return clean_int

  @classmethod
  def _sift_rid_list(cls, rids: List[T.RecordingId]) -> Tuple[Set[int], Set[Any]]:
    cleaned: Set[int] = set()
    malformed: Set[Any] = set()

    for rid in rids:
      try:
        # _clean_rid handles stripping 'xc', converting to int, and range validation
        val = cls._sanitize_rid(rid)
        cleaned.add(val)
      except (ValueError, TypeError):
        # Catch conversion errors (str with letters) or range validation errors
        malformed.add(rid)

    return cleaned, malformed

  def _warn_failed_ids(self, failed_s: Set[int]) -> None:
    failed = sorted(list(failed_s))
    if len(failed) >= 10:
      failed_str = ', '.join([*[str(i) for i in failed[:10]], '...', str(failed[-1])]) + f' (total: {len(failed)})'
    else:
      failed_str = ', '.join(str(i) for i in failed)

    warnings.warn(f'Failed to fetch the following ids: {failed_str}')

  def _warn_malformed_ids(self, malformed: List[int]) -> None:
    malformed_str = [f'{m}' for m in malformed]
    warnings.warn(
      f'Skipping invalid XC recording catalogue numbers - see https://xeno-canto.org/explore/api for more info; {malformed_str}'
    )

  def _search_id_range(
    self,
    start: int,
    end: int,
  ) -> Iterator[Tuple[int, Optional[XenoCantoRecordingSchema]]]:
    batch_size = self._XC_MAX_PAGE_SIZE

    for i in range(start, end + 1, batch_size):
      j = min(i + batch_size - 1, end)
      expected_ids = set(range(i, j + 1))
      received_ids = set()

      try:
        recordings = self._search({'nr': f'{i}-{j}'})

        for r in recordings:
          rid = int(r.number)
          received_ids.add(rid)
          yield rid, r

        missing_ids = expected_ids - received_ids
        for mid in sorted(missing_ids):
          yield mid, None

      except Exception as e:
        if self._verbose:
          warnings.warn(f'Error fetching range {i}-{j}: {e}')

        for failed_id in sorted(expected_ids):
          yield failed_id, None

  def _search_id_scattered(self, rids: List[int]) -> Iterator[Tuple[int, Optional[XenoCantoRecordingSchema]]]:
    for rid in rids:
      try:
        res = self._fetch_one_by_id(rid)

        yield rid, res

      except Exception as e:
        if self._verbose:
          warnings.warn(f'Error fetching ID {rid}: {e}')

        yield rid, None

  def _sample(self, k: int) -> List[XenoCantoRecordingSchema]:
    res: List[XenoCantoRecordingSchema] = []
    seen = set()

    while len(res) < k:
      needed = k - len(res)
      batch_ids = []
      while len(batch_ids) < (needed * 2):
        rid = random.randint(1, self._XC_MAX_ID)
        if rid not in seen:
          batch_ids.append(rid)
          seen.add(rid)

      for _, recording in self._search_id_scattered(batch_ids):  # _search_ids_scattered or _search_ids_range?
        if recording:
          res.append(recording)
        if len(res) >= k:
          break

    return sorted(random.sample(res, k), key=lambda r: r.id)  # type: ignore

  def _fetch_one_by_id(self, rid: int):
    recordings = self._search({'nr': rid})
    try:
      return next(recordings)

    except StopIteration:
      return None

  def _download_promise(self, file_dl: str) -> bytes:
    resp = self._download_session.get(file_dl)
    resp.raise_for_status()
    return resp.content

  def _map(self, rs: Iterable[XenoCantoRecordingSchema], mode: ReturnMode, lean: bool = False) -> Iterator[AnyRecord]:
    match (mode, lean):
      case ('dataclass', True):
        yield from (XenoCantoRecordingLean.from_pydantic(r) for r in rs)
      case ('dataclass', False):
        yield from (XenoCantoRecording.from_pydantic(r) for r in rs)

      case ('dict', True):
        yield from (r.model_dump(mode='python', include=self._LEAN_FIELDS) for r in rs)
      case ('dict', False):
        yield from (r.model_dump(mode='python') for r in rs)

      case _:
        raise ValueError(mode)

  ###################### Public API

  def search(self, **kwargs: Unpack[SearchQueryParams]) -> Union[Iterator[AnyRecord], List[AnyRecord]]:
    limit = kwargs.pop('limit', 500)
    mode = kwargs.pop('mode', 'dataclass')
    lean = kwargs.pop('lean', False)
    stream = kwargs.pop('stream', False)
    cached = kwargs.pop('cached', False)

    query = XenoCantoQuerySchema.model_validate(kwargs)

    rs = self._search(query, limit)

    it = self._map(rs, mode, lean)

    return it if stream else list(it)

  def search_ids(
    self,
    rids: List[T.RecordingId],
    mode: ReturnMode = 'dataclass',
    lean: bool = False,
    stream: bool = False,
  ) -> Union[Iterator[AnyRecord], List[AnyRecord]]:
    ok_ids, malformed = self._sift_rid_list(rids)

    if malformed and self._verbose:
      self._warn_malformed_ids(list(malformed))

    failed_ids: Set[int] = set()

    def _generator():
      def _stream_and_filter() -> Iterator[XenoCantoRecordingSchema]:
        # Consumes the refactored private method
        for rid, record in self._search_id_scattered(list(ok_ids)):
          if record is None:
            failed_ids.add(rid)
          else:
            yield record

      try:
        yield from self._map(_stream_and_filter(), mode, lean)
      finally:
        if self._verbose and failed_ids:
          self._warn_failed_ids(failed_ids)

    gen = _generator()
    if stream:
      return gen

    results = list(gen)

    def sort_key(item: Any):
      if isinstance(item, dict):
        return int(item.get('id', 0))
      return int(getattr(item, 'id', 0))

    try:
      results.sort(key=sort_key)
    except (ValueError, TypeError):
      pass

    return results

  def search_id_range(
    self,
    start: int,
    stop: int,
    mode: ReturnMode = 'dataclass',
    lean: bool = False,
    stream: bool = False,
  ) -> Union[Iterator[AnyRecord], List[AnyRecord]]:
    self._sanitize_rid(start)
    self._sanitize_rid(stop)

    if start > stop:
      raise ValueError('Start ID must be less than or equal to stop ID.')

    failed_ids: Set[int] = set()

    def _generator():
      def _stream_and_filter():
        # Consumption of the private method
        for rid, record in self._search_id_range(start, stop):
          if record is None:
            failed_ids.add(rid)
          else:
            yield record

      try:
        yield from self._map(_stream_and_filter(), mode, lean)

      finally:
        if self._verbose and failed_ids:
          self._warn_failed_ids(failed_ids)

    gen = _generator()
    if stream:
      return gen

    results = list(gen)

    try:
      results.sort(key=lambda x: getattr(x, 'id', 0) if not isinstance(x, dict) else x.get('id', 0))

    except (AttributeError, KeyError):
      pass

    return results

  def get_by_id(self, rid: T.RecordingId, mode: ReturnMode = 'dataclass', lean: bool = False) -> Optional[AnyRecord]:
    srid = self._sanitize_rid(rid)

    if r := self._fetch_one_by_id(srid):
      return list(self._map([r], mode, lean)).pop(0)

  def sample(self, k: int, mode: ReturnMode = 'dataclass', lean: bool = False) -> List[AnyRecord]:
    if not 1 <= k <= 500:
      raise ValueError(k)
    rs = self._sample(k)
    return list(self._map(rs, mode, lean))

  from datetime import datetime

  def download(
    self,
    recordings: Union[List[XenoCantoRecord], Iterator[XenoCantoRecord], List[int]],
    target_dir: Optional[Union[str, Path]] = None,
    grouping: Literal['flat', 'species', 'recordist'] = 'flat',
    naming: Literal['original', 'catalogue'] = 'original',
    replace_ws: bool = False,
    sep: str = '-',
  ):
    rs_list: Union[List[XenoCantoRecord], List[int]] = list(recordings)
    rs: List[XenoCantoRecord] = []

    if not recordings:
      return

    if isinstance(rs_list[0], int):
      fetched = self._search_id_scattered(rs_list)  # type: ignore
      rs = [r for _, r in fetched if r is not None]

    else:
      rs = rs_list

    if target_dir is None:
      # Generate safe timestamp: 2026-01-02T13-57-53
      timestamp = datetime.now().isoformat(timespec='seconds').replace(':', '-')
      master_dir = Path.cwd() / f'xc-recordings-{timestamp}'
    else:
      master_dir = Path(target_dir)

    master_dir.mkdir(parents=True, exist_ok=True)

    for r in rs:
      if grouping == 'species':
        to_dir = master_dir / (r.genus + sep + r.epithet).lower()

      elif grouping == 'recordist':
        if r.recordist is not None:
          to_dir = master_dir / r.recordist.lower()
        else:
          to_dir = master_dir / 'unknown'

      else:
        to_dir = master_dir

      to_dir.mkdir(exist_ok=True)

      path = to_dir / r.file_name

      if naming == 'catalogue':
        path = path.with_stem(str(r.number))

      path.write_bytes(r.f)
