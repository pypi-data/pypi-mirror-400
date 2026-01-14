from pydantic import BaseModel, Field
from typing import List, Any


class XenoCantoResponseSchema(BaseModel):
  num_recordings: int = Field(
    alias='numRecordings',
    description='Total recordings fetched via the query',
  )
  num_species: int = Field(
    alias='numSpecies',
    description='Number of species represented in the results',
  )
  page: int = Field(
    alias='page',
    description='Current page number in the query result',
  )
  num_pages: int = Field(
    alias='numPages',
    description='Total pages of recordings fetched via the query',
  )
  recordings: List[Any] = Field(
    description='Raw list of recording objects on this page',
  )

  def __bool__(self):
    return bool(self.recordings)
