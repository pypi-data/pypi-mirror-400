import os
import soundfile as sf
import numpy as np

SRC_DIR = 'wavs_22050_mono'
DST_DIR = 'wavs_22050_int16'

os.makedirs(DST_DIR, exist_ok=True)

for fname in os.listdir(SRC_DIR):
    if fname.lower().endswith('.wav'):
        src_path = os.path.join(SRC_DIR, fname)
        dst_path = os.path.join(DST_DIR, fname)
        
        # Load audio
        data, sr = sf.read(src_path)
        
        # Convert to int16 (scale to [-32768, 32767] range)
        data_int16 = (data * 32767).astype(np.int16)
        
        # Save as int16
        sf.write(dst_path, data_int16, sr, subtype='PCM_16')
        print(f"Converted {fname} to int16")

print("Done converting all files to int16.") 