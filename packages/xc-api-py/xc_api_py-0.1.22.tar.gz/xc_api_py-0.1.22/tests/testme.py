from xeno_canto import Client, tags

from datetime import timedelta
import dotenv
from rich import print

env = dotenv.dotenv_values()

client = Client(env.get('XC_API_KEY'))  # type: ignore

# target_species = [
#   'acrocephalus melanopogon',
#   'acrocephalus arundinaceus',
#   'pycnonotus xanthopygos',
#   'anthus cervinus',
#   'ardea cinerea',
#   'buteo buteo',
#   'columba livia',
#   'coturnix coturnix',
#   'hirundo rustica',
#   'halcyon smyrnensis',
# ]

rs = client.search(
  # length=tags.LengthTag.exactly(19.8),
  quality=tags.QualityTag.at_most('D'),
  country=tags.CountryTag('ch'),
  mode='dataclass',
)
print(rs[:5])
