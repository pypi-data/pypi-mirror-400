"""Xeno-Canto API"""

__version__ = '0.1.0'

from .client.client import Client
from .tags import tags
from .recording.recording import (
  XenoCantoRecording,
  XenoCantoRecordingLean,
)

__all__ = [
  'Client',
  'tags',
  'XenoCantoRecording',
  'XenoCantoRecordingLean',
]
