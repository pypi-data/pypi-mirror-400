import os
import librosa
import soundfile as sf

SRC_DIR = 'wavs'
DST_DIR = 'wavs_22050'
TARGET_SR = 22050

os.makedirs(DST_DIR, exist_ok=True)

for fname in os.listdir(SRC_DIR):
    if fname.lower().endswith('.wav'):
        src_path = os.path.join(SRC_DIR, fname)
        dst_path = os.path.join(DST_DIR, fname)
        y, sr = librosa.load(src_path, sr=None)
        if sr != TARGET_SR:
            y_resampled = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SR)
            sf.write(dst_path, y_resampled, TARGET_SR)
            print(f"Resampled {fname} from {sr} Hz to {TARGET_SR} Hz.")
        else:
            sf.write(dst_path, y, sr)
            print(f"Copied {fname} (already {TARGET_SR} Hz).")
print("Done.") 