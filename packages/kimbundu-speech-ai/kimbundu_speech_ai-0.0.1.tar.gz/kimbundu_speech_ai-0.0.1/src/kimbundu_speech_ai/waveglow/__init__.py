# Make waveglow a subpackage so it can be imported as kimbundu_tts.waveglow
from . import glow
__all__ = ['glow']
