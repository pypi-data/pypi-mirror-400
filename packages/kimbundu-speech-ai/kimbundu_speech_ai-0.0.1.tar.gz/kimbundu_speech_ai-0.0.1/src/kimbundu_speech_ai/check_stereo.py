import torch
from utils import load_wav_to_torch
import os

stereo_files = []
for f in os.listdir('wavs_22050_int16'):
    if f.endswith('.wav'):
        try:
            audio, sr = load_wav_to_torch(f'wavs_22050_int16/{f}')
            if len(audio.shape) > 1:
                stereo_files.append(f)
                print(f'Stereo file: {f}, shape: {audio.shape}')
        except Exception as e:
            print(f'Error with {f}: {e}')

print(f'Found {len(stereo_files)} stereo files') 