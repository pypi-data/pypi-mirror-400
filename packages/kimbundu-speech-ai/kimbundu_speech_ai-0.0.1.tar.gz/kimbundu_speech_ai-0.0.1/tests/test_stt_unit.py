import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, "C:/Users/rsabino/Documents/projecto final/kutanga/tts_package/src")

from kimbundu_speech_ai import STT
import numpy as np
import torch


@pytest.mark.unit
def test_convert_to_text_audio_not_found():
    with patch("kimbundu_speech.stt.librosa.load", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            STT.convert_to_text("missing.wav", "checkpoint path")


@pytest.mark.unit
def test_convert_to_text_checkpoint_not_found():
    with patch("kimbundu_speech.stt.librosa.load",
               return_value=([0.0], 16000)), \
         patch("kimbundu_speech.stt._Internal.load_model_processor",
               side_effect=FileNotFoundError("Checkpoint path does not exist")):

        with pytest.raises(FileNotFoundError):
            STT.convert_to_text("audio.wav", "missing_checkpoint")


@pytest.mark.unit
def test_convert_to_text_success():
    fake_audio = np.zeros(16000)
    fake_sample_rate = 16000

    fake_model = MagicMock()
    fake_processor = MagicMock()

    fake_inputs = MagicMock()
    fake_inputs.input_features = torch.randn(1, 80, 300)

    fake_model.generate.return_value = torch.tensor([[1, 2, 3]])
    fake_processor.return_value = fake_inputs
    fake_processor.batch_decode.return_value = ["  ngana nzambi  "]

    with patch("kimbundu_speech.stt.librosa.load",
               return_value=(fake_audio, fake_sample_rate)), \
         patch("kimbundu_speech.stt._Internal.load_model_processor",
               return_value=(fake_model, fake_processor)):

        result = STT.convert_to_text(
            audio_path="fake.wav",
            checkpoint_path="fake_checkpoint"
        )

    assert result == "ngana nzambi"