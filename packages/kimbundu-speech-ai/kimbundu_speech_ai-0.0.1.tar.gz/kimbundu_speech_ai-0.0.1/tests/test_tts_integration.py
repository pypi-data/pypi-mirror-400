import sys

sys.path.insert(0, "C:/Users/rsabino/Documents/projecto final/kutanga/tts_package/src")

from kimbundu_speech_ai import TTS
from pathlib import Path
import pytest
import os
import soundfile as sf


@pytest.mark.integration
def test_convert_to_file_creates_valid_wav():
    checkpoint_path = Path("./tests/models/checkpoint_50500")
    waveglow_path = Path("./tests/models/waveglow.pt")

    assert checkpoint_path.exists()
    assert waveglow_path.exists()

    result = TTS.convert_to_file(
        text="nzambi",
        checkpoint_path=checkpoint_path,
        waveglow_path=waveglow_path,
    )

    assert os.path.exists(result)

    audio, sr = sf.read(result)

    assert audio.ndim == 1
    assert audio.size > 0
    assert sr > 0


@pytest.mark.integration
def test_play_default_player_runs(monkeypatch, tmp_path):
    checkpoint_path = Path("./tests/models/checkpoint_50500")
    waveglow_path = Path("./tests/models/waveglow.pt")

    assert checkpoint_path.exists()
    assert waveglow_path.exists()

    monkeypatch.setattr("kimbundu_speech.tts.os.system", lambda *_: 0)

    TTS.play_default_player(
        text="nzambi",
        checkpoint_path=checkpoint_path,
        waveglow_path=waveglow_path,
    )