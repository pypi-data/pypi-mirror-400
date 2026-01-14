import sys

sys.path.insert(0, "C:/Users/rsabino/Documents/projecto final/kutanga/tts_package/src")

from kimbundu_speech_ai import STT
from pathlib import Path
import pytest


@pytest.mark.integration
def test_check_transcription_correct():
    audio_path = Path("./tests/data/sample.wav")
    checkpoint_path = Path("./tests/models/stt-model")

    assert audio_path.exists()
    assert checkpoint_path.exists()

    transcription = STT.convert_to_text(
        audio_path=audio_path.absolute(),
        checkpoint_path=checkpoint_path.absolute(),
    )

    assert isinstance(transcription, str)
    assert len(transcription) > 0

    assert transcription == "ngana nzambi"