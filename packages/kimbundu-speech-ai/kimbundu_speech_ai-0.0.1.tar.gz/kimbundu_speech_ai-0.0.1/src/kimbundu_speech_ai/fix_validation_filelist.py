# Read the validation filelist and update paths
with open('filelists/ljs_audio_text_val_filelist.txt', 'r') as f:
    lines = f.readlines()

# Update paths from wavs_22050/ to wavs_22050_int16/
updated_lines = []
for line in lines:
    if line.startswith('wavs_22050/'):
        updated_line = line.replace('wavs_22050/', 'wavs_22050_int16/')
        updated_lines.append(updated_line)
    else:
        updated_lines.append(line)

# Write the updated validation filelist
with open('filelists/ljs_audio_text_val_filelist.txt', 'w') as f:
    f.writelines(updated_lines)

print(f"Updated validation filelist with {len(updated_lines)} files") 