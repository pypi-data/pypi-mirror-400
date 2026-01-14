import torch
import numpy as np
from utils import load_wav_to_torch
from kimbundu_speech_ai.layers import TacotronSTFT

# Test with the first file in the filelist
filename = 'wavs_22050_int16/1.wav'
print(f"Testing file: {filename}")

try:
    audio, sampling_rate = load_wav_to_torch(filename)
    print(f"Audio shape: {audio.shape}, dtype: {audio.dtype}")
    print(f"Sample rate: {sampling_rate}")
    print(f"Audio tensor size: {audio.numel()}")

    # Test normalization
    max_wav_value = 32768.0
    audio_norm = audio / max_wav_value
    print(f"Normalized audio shape: {audio_norm.shape}, dtype: {audio_norm.dtype}")

    # Test unsqueeze
    audio_norm = audio_norm.unsqueeze(0)
    print(f"Unsqueezed audio shape: {audio_norm.shape}")
    print(f"Unsqueezed tensor size: {audio_norm.numel()}")

    # Test STFT
    stft = TacotronSTFT(
        filter_length=1024,
        hop_length=256,
        win_length=1024,
        n_mel_channels=80,
        sampling_rate=22050,
        mel_fmin=0.0,
        mel_fmax=8000.0
    )

    melspec = stft.mel_spectrogram(audio_norm)
    print(f"Mel spectrogram shape: {melspec.shape}")
    print("SUCCESS: Audio processing worked!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc() 