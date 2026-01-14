import os
import sys
from typing import Optional, Tuple

import numpy as np
import torch
import soundfile as sf

# Ensure the package directory is on sys.path so the repo's modules can be imported
pkg_dir = os.path.dirname(__file__)
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

# Use a relative import so `from kimbundu_tts import TTS` exposes the module
from . import tts as TTS
from . import stt as STT

__all__ = [
    'TTS',
    'STT'
]