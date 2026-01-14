from xeno_canto.types import QualityRating
from xeno_canto.tags.search_tag import SearchTag
from xeno_canto.tags.numeric_tag import (
  NumericTag,
  NumericRangeTag,
)
from xeno_canto.tags.tag_types import (
  Numeric,
  Contraint,
)

from typing import (
  Union,
  Optional,
  overload,
  Any,
  Tuple,
)
import datetime
import pycountry
from pycountry.db import Country


class CountryTag(SearchTag):
  def __init__(self, country_identifier: str):
    try:
      ct: Country = pycountry.countries.lookup(country_identifier)  # type: ignore

    except Exception:
      raise ValueError(
        f'Invalid country argument "{country_identifier}"; Pass a valid country name or ISO code'
      ) from None

    self.name = ct.name.lower()
    self.alpha_2 = ct.alpha_2.lower()
    self.alpha_3 = ct.alpha_3.lower()


class BoxTag(SearchTag):
  ay: float
  ax: float
  by: float
  bx: float

  @overload
  def __init__(self, sw: Tuple[float, float], ne: Tuple[float, float]): ...

  @overload
  def __init__(self, lat_min: float, lon_min: float, lat_max: float, lon_max: float): ...

  def __init__(self, *args: Any):  # type: ignore
    if len(args) == 2:
      sw, ne = args
      self.ay, self.ax = sw
      self.by, self.bx = ne

    elif len(args) == 4:
      self.ay, self.ax, self.by, self.bx = args

    else:
      raise TypeError('Invalid arguments provided to BoxTag')


class LengthTag(NumericRangeTag): ...


class SampleRateTag(NumericTag): ...


class QualityTag(NumericRangeTag):
  def __init__(
    self,
    a: Union[str, int],
    b: Optional[Union[str, int]] = None,
    constraint: Optional[Contraint] = None,
  ):
    if isinstance(a, str):
      self.a = QualityRating[a.capitalize()]
    else:
      self.a = QualityRating(a)

    if b is not None:
      if isinstance(b, str):
        self.b = QualityRating[b.capitalize()]
      else:
        self.b = QualityRating(b)

    self.constraint = constraint

  @classmethod
  def between(cls, a: Union[str, int], b: Union[str, int]):
    raise NotImplementedError()  # TODO

  @classmethod
  def at_least(cls, v: Union[str, int]):
    return cls(v, constraint='at least')

  @classmethod
  def at_most(cls, v: Union[str, int]):
    return cls(v, constraint='at most')


class SinceTag(SearchTag):
  def __init__(self, value: Union[Numeric, datetime.datetime]):
    self.value = value
