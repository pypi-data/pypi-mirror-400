# Read the training filelist
with open('filelists/ljs_audio_text_train_filelist.txt', 'r') as f:
    training_lines = f.readlines()

print(f"Total training files: {len(training_lines)}")

# Take the last 10% of files for validation (approximately 126 files)
validation_size = len(training_lines) // 10
validation_lines = training_lines[-validation_size:]

# Write the validation filelist
with open('filelists/ljs_audio_text_val_filelist.txt', 'w') as f:
    f.writelines(validation_lines)

print(f"Created validation filelist with {len(validation_lines)} files")
print(f"Validation files range from: {validation_lines[0].strip().split('|')[0]} to {validation_lines[-1].strip().split('|')[0]}") 