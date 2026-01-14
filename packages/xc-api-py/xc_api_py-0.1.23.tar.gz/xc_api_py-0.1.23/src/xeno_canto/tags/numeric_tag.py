from .search_tag import SearchTag
from .tag_types import Numeric, Contraint

from typing import Optional


class NumericTag(SearchTag):
  def __init__(
    self,
    a: Numeric,
    b: Optional[Numeric] = None,
    constraint: Optional[Contraint] = None,
  ):
    self.a = a
    self.b = b
    self.constraint = constraint

  @classmethod
  def at_least(cls, v: Numeric):
    return cls(v, constraint='at least')  # f'">{value}"'

  @classmethod
  def at_most(cls, value: Numeric):
    return cls(value, constraint='at most')  # f'"<{value}"'

  @classmethod
  def exactly(cls, value: Numeric):
    return cls(value, constraint='exactly')  # f'"={length}"'


class NumericRangeTag(NumericTag):
  @classmethod
  def between(cls, a: Numeric, b: Numeric):
    if not (a and b):
      raise ValueError('Need two values')

    if type(a) is not type(b):
      raise ValueError()

    if a == b:
      raise ValueError(f'Range values must be different: {a}, {b}')

    if a > b:  # type: ignore
      a, b = b, a

    return cls(a, b, constraint='between')
