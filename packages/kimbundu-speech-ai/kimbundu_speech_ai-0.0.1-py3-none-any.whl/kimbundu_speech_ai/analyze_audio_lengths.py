import torch
from utils import load_wav_to_torch
import os
from collections import Counter

# Read the full filelist
with open('filelists/ljs_audio_text_train_filelist_full.txt', 'r') as f:
    lines = f.readlines()

lengths = []
errors = []

print("Analyzing audio lengths...")
for i, line in enumerate(lines):
    if i % 100 == 0:
        print(f"Processed {i}/{len(lines)} files...")
    
    filename = line.strip().split('|')[0]
    try:
        audio, sr = load_wav_to_torch(filename)
        lengths.append(audio.numel())
    except Exception as e:
        errors.append((filename, str(e)))

print(f"\nFound {len(errors)} errors:")
for filename, error in errors[:10]:  # Show first 10 errors
    print(f"  {filename}: {error}")

print(f"\nAudio length distribution:")
length_counts = Counter(lengths)
for length, count in sorted(length_counts.items()):
    print(f"  {length} samples: {count} files")

print(f"\nTotal files analyzed: {len(lengths)}")
print(f"Unique lengths: {len(length_counts)}") 