from abc import ABC
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler


class SearchTag(ABC):
  @classmethod
  def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
    choices = [
      core_schema.is_instance_schema(cls),  # Allow an instance of this class to pass through without validation
      core_schema.any_schema(),  # Allow validation from a dictionary (if needed) or pass to next handler
    ]
    return core_schema.union_schema(
      choices,
      # If you want to use this class as a field *input* type,
      # you would define a parser/validator here.
    )
