import torch
import numpy as np
import soundfile as sf
from kimbundu_speech_ai.hparams import create_hparams
from kimbundu_speech_ai.model import Tacotron2
from kimbundu_speech_ai.text import text_to_sequence
import os
import sys

# Add waveglow directory to Python path (if run standalone)
sys.path.append('./kimbundu_tts/waveglow')

# Find the latest checkpoint
outdir = "newoutdir"
checkpoints = [f for f in os.listdir(outdir) if f.startswith("checkpoint_")]
latest_ckpt = sorted(checkpoints, key=lambda x: int(x.split('_')[-1]))[-1]
checkpoint_path = os.path.join(outdir, latest_ckpt)
print(f"Using checkpoint: {checkpoint_path}")

# Load Tacotron2
hparams = create_hparams("sampling_rate=22050")
model = Tacotron2(hparams)
model.load_state_dict(torch.load(checkpoint_path, map_location='cpu')['state_dict'])
model.eval()

# Prepare input text
text = "a exana phala kukala mundu ua nzambi"
sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
sequence = torch.from_numpy(sequence).long()

# Synthesize mel spectrogram
with torch.no_grad():
    mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
mel = mel_outputs_postnet[0].unsqueeze(0).cpu()

# Load WaveGlow
waveglow = torch.load("waveglow.pt", map_location='cpu')['model']
waveglow.eval()
for m in waveglow.modules():
    if 'Conv' in str(type(m)):
        setattr(m, 'padding_mode', 'zeros')

# Remove weight normalization
from torch.nn.utils import remove_weight_norm
for k in waveglow.convinv:
    try:
        remove_weight_norm(k)
    except ValueError:
        pass
# waveglow.upsample is a ConvTranspose1d, not a list
if hasattr(waveglow.upsample, 'weight_g'):
    try:
        remove_weight_norm(waveglow.upsample)
    except ValueError:
        pass

# Patch torch.randn to always create CPU tensors during inference
orig_randn = torch.randn
def cpu_randn(*args, **kwargs):
    kwargs['device'] = 'cpu'
    return orig_randn(*args, **kwargs)
torch.randn = cpu_randn

# Generate audio
with torch.no_grad():
    audio = waveglow.infer(mel, sigma=0.666)
torch.randn = orig_randn  # Restore original function
audio = audio[0].data.cpu().numpy()
sf.write("output_waveglow.wav", audio, hparams.sampling_rate)
print("Audio saved as output_waveglow.wav") 