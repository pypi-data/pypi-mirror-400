import torch
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
from utils import load_wav_to_torch
from kimbundu_speech_ai.layers import TacotronSTFT

# Test with a file from our filtered list
filename = 'wavs_22050_int16/1.wav'
print(f"Testing file: {filename}")

try:
    # Load audio
    audio, sampling_rate = load_wav_to_torch(filename)
    print(f"Audio shape: {audio.shape}, dtype: {audio.dtype}")
    print(f"Sample rate: {sampling_rate}")
    print(f"Audio tensor size: {audio.numel()}")

    # Normalize
    max_wav_value = 32768.0
    audio_norm = audio / max_wav_value
    print(f"Normalized audio shape: {audio_norm.shape}")

    # Unsqueeze
    audio_norm = audio_norm.unsqueeze(0)
    print(f"Unsqueezed audio shape: {audio_norm.shape}")
    print(f"Unsqueezed tensor size: {audio_norm.numel()}")

    # Create STFT
    stft = TacotronSTFT(
        filter_length=1024,
        hop_length=256,
        win_length=1024,
        n_mel_channels=80,
        sampling_rate=22050,
        mel_fmin=0.0,
        mel_fmax=8000.0
    )

    # Debug the transform method
    print("\n=== Debugging STFT transform ===")
    input_data = audio_norm
    print(f"Input data shape: {input_data.shape}")
    print(f"Input data size: {input_data.numel()}")
    
    num_batches = input_data.size(0)
    num_samples = input_data.size(1)
    print(f"num_batches: {num_batches}")
    print(f"num_samples: {num_samples}")
    
    # This is where the error occurs
    expected_size = num_batches * 1 * num_samples
    actual_size = input_data.numel()
    print(f"Expected size for reshape: {expected_size}")
    print(f"Actual size: {actual_size}")
    
    if expected_size != actual_size:
        print(f"ERROR: Size mismatch! Expected {expected_size}, got {actual_size}")
        print(f"This suggests the tensor has unexpected dimensions")
        
        # Let's check the actual tensor structure
        print(f"Tensor shape: {input_data.shape}")
        print(f"Tensor strides: {input_data.stride()}")
        print(f"Tensor is contiguous: {input_data.is_contiguous()}")
        
        # Try to understand what's happening
        if input_data.numel() == 97020 and num_samples == 48510:
            print("This matches the error! The tensor has size 97020 but num_samples is 48510")
            print("This suggests the tensor might be duplicated or has an extra dimension")
            
            # Check if it's a 2D tensor that should be 1D
            if len(input_data.shape) > 2:
                print(f"Tensor has {len(input_data.shape)} dimensions, might need flattening")
                print(f"Original shape: {audio.shape}")
                print(f"After unsqueeze: {audio_norm.shape}")
    
    # Try the reshape that's causing the error
    try:
        reshaped = input_data.view(num_batches, 1, num_samples)
        print("SUCCESS: Reshape worked!")
        print(f"Reshaped shape: {reshaped.shape}")
    except Exception as e:
        print(f"ERROR in reshape: {e}")
        print(f"Trying to understand the tensor better...")
        
        # Let's try to fix it
        if input_data.numel() == 97020 and num_samples == 48510:
            print("Attempting to fix the tensor...")
            # The tensor might be duplicated, let's try to take half
            if input_data.numel() == 2 * num_samples:
                print("Tensor appears to be duplicated, trying to take first half...")
                fixed_tensor = input_data[:num_samples]
                print(f"Fixed tensor shape: {fixed_tensor.shape}")
                print(f"Fixed tensor size: {fixed_tensor.numel()}")
                
                # Try reshape with fixed tensor
                try:
                    reshaped = fixed_tensor.unsqueeze(0).view(1, 1, num_samples)
                    print("SUCCESS: Reshape worked with fixed tensor!")
                except Exception as e2:
                    print(f"ERROR in reshape with fixed tensor: {e2}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc() 