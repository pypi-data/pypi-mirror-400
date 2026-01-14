import torch
from kimbundu_speech_ai.hparams import create_hparams
from kimbundu_speech_ai.model import Tacotron2
from kimbundu_speech_ai.text import text_to_sequence
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
from librosa.feature.inverse import mel_to_audio

# Set parameters
hparams = create_hparams("sampling_rate=16000")
checkpoint_path = "outdir/checkpoint_600"

# Load model
model = Tacotron2(hparams)
model.load_state_dict(torch.load(checkpoint_path, map_location='cpu')['state_dict'])
model.eval()

# Prepare input text
text = "hello my friend"
sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
sequence = torch.from_numpy(sequence).long()

# Synthesize mel spectrogram
with torch.no_grad():
    mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)

# Save mel spectrogram as an image (optional)
plt.imshow(mel_outputs_postnet[0].cpu().numpy(), aspect='auto', origin='lower')
plt.title("Mel Spectrogram")
plt.savefig("mel_output.png")

# Convert mel to waveform using Griffin-Lim
mel = mel_outputs_postnet[0].cpu().numpy()
wav = mel_to_audio(mel, sr=hparams.sampling_rate, n_fft=hparams.filter_length, hop_length=hparams.hop_length, win_length=hparams.win_length)
sf.write("output.wav", wav, hparams.sampling_rate)
print("Audio saved as output.wav") 