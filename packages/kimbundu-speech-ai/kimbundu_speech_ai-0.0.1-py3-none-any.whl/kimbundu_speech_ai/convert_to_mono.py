import os
import soundfile as sf
import numpy as np

SRC_DIR = 'wavs_22050'
DST_DIR = 'wavs_22050_mono'

os.makedirs(DST_DIR, exist_ok=True)

for fname in os.listdir(SRC_DIR):
    if fname.lower().endswith('.wav'):
        src_path = os.path.join(SRC_DIR, fname)
        dst_path = os.path.join(DST_DIR, fname)
        
        # Load audio
        data, sr = sf.read(src_path)
        
        # Convert stereo to mono by averaging channels
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        
        # Save as mono
        sf.write(dst_path, data, sr)
        print(f"Converted {fname} to mono")

print("Done converting all files to mono.") 