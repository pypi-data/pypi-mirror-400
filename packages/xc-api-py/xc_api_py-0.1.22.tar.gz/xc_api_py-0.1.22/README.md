# Xeno Canto API Client for Python

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![Pydantic](https://img.shields.io/badge/data-Pydantic-red)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intuitive, type-safe Python wrapper for the [Xeno-Canto API](https://xeno-canto.org/api/3).  
Streamline your bioacoustics and machine learning workflows by searching, filtering, and processing wildlife recordings with full validation and IDE autocompletion.  

## Project Sponsors
<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/yuvalrot479/xc-api-py/main/.github/asp-lab-logo.jpg" alt="asp-lab-logo"></td>
    <td><img src="https://raw.githubusercontent.com/yuvalrot479/xc-api-py/main/.github/tel-hai-logo.png" alt="tel-hai-logo"></td>
  </tr>
</table>

## Disclaimer
This project is a free and open-source tool intended for educational purposes only;  
This project is provided AS IS without any warranty - use at your own risk;  
This project is not associated with, maintained by, or endorsed by the [Xeno-Canto Foundation](https://xeno-canto.org/);  
Users are responsible for adhering to the [Xeno-Canto Terms of Use](https://xeno-canto.org/about/terms) and respecting the licensing of individual recordings.  

## Quickstart

### Installation

> It is highly recommended to use a **virtual environment** to manage your project's dependencies and avoid conflicts with system-wide packages.
> 
> **Creating a virtual environment:**
> ```bash
> # Create the environment
> python -m venv .venv
> 
> # Activate it (macOS/Linux)
> source .venv/bin/activate
> 
> # Activate it (Windows)
> .venv\Scripts\activate
> ```
> For more details, see the official [Python guide on Virtual Environments](https://docs.python.org/3/library/venv.html).

#### PIP
```bash
pip install xc-api-py
```

### Basic Usage

```python
from xeno_canto import Client

client = Client(api_key='YOUR_API_KEY')

# Search for multiple species at once
recordings = client.search(
    species_list=['Grus grus', 'Acrocephalus melanopogon'], 
    limit=50
)

# Download and organize automatically
client.download(
    recordings, 
    grouping='species', 
    naming='catalogue'
)
```

## Advanced Features

### Bulk Downloading & Organization
The `download` method supports advanced path management and naming conventions to keep your datasets organized for machine learning or archival.

| Argument | Options | Description |
| :--- | :--- | :--- |
| `grouping` | `'flat'`, `'species'`, `'recordist'` | Nest files in subdirs (e.g., `genus-species/subspecies/file.mp3`). |
| `naming` | `'original'`, `'catalogue'` | Use uploader filename or standardized `xc12345.mp3`. |
| `target_dir` | `str` or `Path` | If `None`, creates a timestamped folder: `xc-recordings-YYYY-MM-DD...` |

```python
# Create a recordist-based dataset with standardized names
client.download(
    recordings, 
    target_dir='./my_dataset',
    grouping='recordist',
    naming='catalogue'
)
```

### Flexible Search
The `search` method supports iterative species lists, coordinate filtering, and streaming for large datasets.

```python
# Search across multiple species with a global limit and streaming
rs = client.search(
    species_list=['Passer domesticus', 'Passer montanus'],
    country='israel',
    limit=100,
    stream=True
)
```

### Data Return Modes & "Lean" Objects
You can control exactly what kind of objects the client returns using the `mode` and `lean` parameters. 

The `lean=True` flag optimizes performance by filtering out dozens of metadata fields (like location descriptions, temperature, or uploader comments) and returning only the critical core needed for identification and file retrieval.



| Mode | Return Type | Best For |
| :--- | :--- | :--- |
| **`dataclass`** (default) | `XenoCantoRecording` | Fast script performance |
| **`pydantic`** | `XenoCantoRecordingSchema` | Strict runtime validation |
| **`audio`** | `XenoCantoAudio` | Direct playback and processing |
| **`dict`** | `dict` | Loading into Pandas DataFrames |
| **`json`** | `str` | Raw archival/caching |

```python
# High-speed search returning lean dataclasses
recordings = client.search(genus='apus', mode='dataclass', lean=True)
```

### SoundDevice Playback
```python
import sounddevice as sd
from xeno_canto import Client

client = Client('API_KEY')
# mode='audio' returns XenoCantoAudio objects
recording = client.get_by_id('XC125492', mode='audio')

with recording.load() as a:
    sd.play(a.to_numpy(), a.sample_rate)
    sd.wait()
```

### BirdNET Integration
```python
from birdnetlib.analyzer import Analyzer
from birdnetlib import RecordingBuffer

analyzer = Analyzer()
recording = client.get_by_id('XC779948', mode='audio')

with recording.load() as a:
    # Segment audio for BirdNET (expects 48kHz)
    arr = a.to_birdnet() 
    
buffer = RecordingBuffer(analyzer, arr)
buffer.analyze()
print(buffer.detections)
```

## License
Distributed under the MIT License. See `LICENSE` for more information.
