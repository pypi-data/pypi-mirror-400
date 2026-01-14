#!/usr/bin/env python3

import sys
import traceback
import torch
from utils import load_wav_to_torch
from hparams import create_hparams
import layers

def test_stft():
    try:
        # Create hparams
        hparams = create_hparams("training_files=train_filelist.txt,validation_files=val_filelist.txt")
        
        # Create STFT layer
        print("Creating STFT layer...")
        stft = layers.TacotronSTFT(
            hparams.filter_length, hparams.hop_length, hparams.win_length,
            hparams.n_mel_channels, hparams.sampling_rate, hparams.mel_fmin,
            hparams.mel_fmax)
        print("STFT layer created successfully")
        
        # Load audio
        print("Loading audio...")
        audio, sampling_rate = load_wav_to_torch('wavs/audio1.wav')
        print(f"Audio loaded: shape={audio.shape}, sr={sampling_rate}")
        
        # Check sampling rate
        print(f"Expected SR: {stft.sampling_rate}, Actual SR: {sampling_rate}")
        if sampling_rate != stft.sampling_rate:
            print("Sampling rate mismatch!")
            return
        
        # Normalize audio
        print("Normalizing audio...")
        audio_norm = audio / hparams.max_wav_value
        audio_norm = audio_norm.unsqueeze(0)
        audio_norm = torch.autograd.Variable(audio_norm, requires_grad=False)
        print(f"Normalized audio shape: {audio_norm.shape}")
        
        # Generate mel spectrogram
        print("Generating mel spectrogram...")
        melspec = stft.mel_spectrogram(audio_norm)
        print(f"Mel spectrogram shape: {melspec.shape}")
        
        # Squeeze
        melspec = torch.squeeze(melspec, 0)
        print(f"Final mel shape: {melspec.shape}")
        
        print("Success!")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_stft() 