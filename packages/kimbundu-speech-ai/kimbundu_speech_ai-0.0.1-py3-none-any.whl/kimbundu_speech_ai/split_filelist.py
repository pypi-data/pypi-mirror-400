import random

# Read the full filelist (use train_filelist.txt as the source since both are the same)
with open('train_filelist.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

random.shuffle(lines)

split_idx = int(0.8 * len(lines))
train_lines = lines[:split_idx]
val_lines = lines[split_idx:]

with open('train_filelist.txt', 'w', encoding='utf-8') as f:
    for line in train_lines:
        f.write(line + '\n')

with open('val_filelist.txt', 'w', encoding='utf-8') as f:
    for line in val_lines:
        f.write(line + '\n')

print(f"Split {len(lines)} lines into {len(train_lines)} training and {len(val_lines)} validation samples.") 