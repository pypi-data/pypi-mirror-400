import torch
from utils import load_wav_to_torch

# Read the original filelist
with open('filelists/ljs_audio_text_train_filelist.txt', 'r') as f:
    lines = f.readlines()

# Filter to only include files with 95232 samples
filtered_lines = []
for line in lines:
    filename = line.strip().split('|')[0]
    try:
        audio, sampling_rate = load_wav_to_torch(filename)
        if audio.numel() == 95232:
            filtered_lines.append(line)
            print(f"✓ {filename}: {audio.numel()} samples")
        else:
            print(f"✗ {filename}: {audio.numel()} samples (skipped)")
    except Exception as e:
        print(f"✗ {filename}: ERROR - {e}")

# Write filtered filelist
with open('filelists/ljs_audio_text_train_filelist_filtered.txt', 'w') as f:
    f.writelines(filtered_lines)

print(f"\nFiltered filelist created with {len(filtered_lines)} files (out of {len(lines)} total)")
print("Copying to main filelist...")

# Copy to main filelist
import shutil
shutil.copy('filelists/ljs_audio_text_train_filelist_filtered.txt', 'filelists/ljs_audio_text_train_filelist.txt')

print("Done!") 