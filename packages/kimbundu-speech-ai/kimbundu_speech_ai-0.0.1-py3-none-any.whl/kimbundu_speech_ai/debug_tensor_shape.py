import torch
from utils import load_wav_to_torch
import os

problematic_files = []
for f in os.listdir('wavs_22050_int16'):
    if f.endswith('.wav'):
        try:
            audio, sr = load_wav_to_torch(f'wavs_22050_int16/{f}')
            if audio.numel() == 97020 and audio.shape[0] == 48510:
                problematic_files.append(f)
                print(f'Problematic file: {f}, shape: {audio.shape}, numel: {audio.numel()}')
        except Exception as e:
            print(f'Error with {f}: {e}')

print(f'Found {len(problematic_files)} problematic files') 