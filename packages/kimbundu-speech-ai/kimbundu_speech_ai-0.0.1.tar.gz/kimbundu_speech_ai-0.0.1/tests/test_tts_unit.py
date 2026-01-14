import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, "C:/Users/rsabino/Documents/projecto final/kutanga/tts_package/src")

from kimbundu_speech_ai import TTS
import numpy as np


@pytest.mark.unit
def test_convert_to_file_writes_audio():
    fake_audio = np.zeros(100)
    fake_hparams = MagicMock(sampling_rate=22050)

    with patch("kimbundu_speech.tts._Internal.get_audio_hparams",
               return_value=(fake_audio, fake_hparams)), \
         patch("kimbundu_speech.tts.sf.write") as mock_write:

        TTS.convert_to_file(
            text="nzambi",
            checkpoint_path="ckpt",
            waveglow_path="wg.pt",
            out_wav="out.wav"
        )

        mock_write.assert_called_once_with(
            "out.wav",
            fake_audio,
            22050
        )


@pytest.mark.unit
def test_convert_to_file_returns_path():
    with patch("kimbundu_speech.tts._Internal.get_audio_hparams",
               return_value=(np.zeros(10), MagicMock(sampling_rate=22050))), \
         patch("kimbundu_speech.tts.sf.write"):

        result = TTS.convert_to_file(
            text="nzambi",
            checkpoint_path="ckpt",
            waveglow_path="wg.pt",
            out_wav="audio.wav"
        )

        assert result == "audio.wav"


@pytest.mark.unit
def test_play_default_player_audio_generation_failed():
    with patch("kimbundu_speech.tts._Internal.get_audio_hparams",
               side_effect=RuntimeError("generation failed")):

        with pytest.raises(RuntimeError):
            TTS.play_default_player(
                text="nzambi",
                checkpoint_path="ckpt",
                waveglow_path="wg.pt"
            )