import os
import sys
from typing import Optional, Tuple

import numpy as np
import torch
import soundfile as sf
import tempfile
import platform

# Ensure the package directory is on sys.path so the repo's modules can be imported
pkg_dir = os.path.dirname(__file__)
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

from kimbundu_speech_ai.hparams import create_hparams
from kimbundu_speech_ai.model import Tacotron2
from kimbundu_speech_ai.text import text_to_sequence

class _Internal:
    @staticmethod
    def load_tacotron(model_path: str, hparams_overrides: Optional[str] = None, device: str = 'cpu') -> Tuple[Tacotron2, object]:
        hparams = create_hparams(hparams_overrides or "sampling_rate=22050")
        model = Tacotron2(hparams)
        state = torch.load(model_path, map_location=device)
        if 'state_dict' in state:
            model.load_state_dict(state['state_dict'])
        else:
            model.load_state_dict(state)
        model.to(device)
        model.eval()
        return model, hparams
    
    @staticmethod
    def synthesize_mel(model: Tacotron2, text: str, device: str = 'cpu') -> torch.Tensor:
        sequence = np.array(text_to_sequence(text))[None, :]
        sequence = torch.from_numpy(sequence).long().to(device)
        with torch.no_grad():
            mel_outputs, mel_outputs_postnet, _, _ = model.inference(sequence)
        mel = mel_outputs_postnet[0].unsqueeze(0).cpu()
        return mel
    
    @staticmethod
    def maybe_resolve_waveglow_path(path: str) -> str:
        if os.path.isdir(path):
            candidate = os.path.join(path, 'waveglow.pt')
            if os.path.exists(candidate):
                return candidate
        return path
    
    @staticmethod
    def load_waveglow(waveglow_model_path: str, device: str = 'cpu'):
        waveglow_model_path = _Internal.maybe_resolve_waveglow_path(waveglow_model_path)
        # Ensure waveglow module files are importable so torch.load can unpickle custom classes
        waveglow_dir = os.path.join(os.path.dirname(__file__), 'waveglow')
        if os.path.isdir(waveglow_dir) and waveglow_dir not in sys.path:
            sys.path.insert(0, waveglow_dir)

        # Try to allowlist WaveGlow class for torch's safe unpickling when available.
        # Prefer importing the module as a subpackage when installed: `kimbundu_tts.waveglow.glow`.
        allowed_globals = []
        try:
            from kimbundu_speech_ai.waveglow import glow as _glow
            if hasattr(_glow, 'WaveGlow'):
                allowed_globals.append(_glow.WaveGlow)
        except Exception:
            try:
                import glow as _glow  # fallback to top-level glow (for editable runs)
                if hasattr(_glow, 'WaveGlow'):
                    allowed_globals.append(_glow.WaveGlow)
            except Exception:
                pass

        state = None
        ser = torch.serialization
        try:
            if hasattr(ser, 'safe_globals') and allowed_globals:
                with ser.safe_globals(allowed_globals):
                    state = torch.load(waveglow_model_path, map_location=device, weights_only=False)
            elif hasattr(ser, 'add_safe_globals') and allowed_globals:
                ser.add_safe_globals(allowed_globals)
                state = torch.load(waveglow_model_path, map_location=device)
            else:
                # Fallback: try full load (may raise on newer torch versions)
                state = torch.load(waveglow_model_path, map_location=device)
        except TypeError:
            # Older torch that doesn't accept weights_only arg
            state = torch.load(waveglow_model_path, map_location=device)
        # torch checkpoints from some scripts wrap model under 'model'
        if isinstance(state, dict) and 'model' in state:
            waveglow = state['model']
        else:
            waveglow = state
        waveglow.to(device)
        waveglow.eval()
        for m in waveglow.modules():
            if 'Conv' in str(type(m)):
                setattr(m, 'padding_mode', 'zeros')

        # Remove weight norm if present
        from torch.nn.utils import remove_weight_norm
        if hasattr(waveglow, 'convinv'):
            for k in waveglow.convinv:
                try:
                    remove_weight_norm(k)
                except Exception:
                    pass
        if hasattr(waveglow, 'upsample'):
            try:
                remove_weight_norm(waveglow.upsample)
            except Exception:
                pass
        return waveglow
    
    @staticmethod
    def waveglow_infer_to_numpy(waveglow, mel: torch.Tensor, sigma: float = 0.666, device: str = 'cpu') -> np.ndarray:
        # Ensure mel is on the same device
        mel = mel.to(device)
        orig_randn = torch.randn

        def cpu_randn(*args, **kwargs):
            kwargs['device'] = device
            return orig_randn(*args, **kwargs)

        torch.randn = cpu_randn
        with torch.no_grad():
            audio = waveglow.infer(mel, sigma=sigma)
        torch.randn = orig_randn
        audio = audio[0].data.cpu().numpy()
        return audio
    
    @staticmethod
    def get_audio_hparams(model_path: str, waveglow_model_path: str, text: str, device: str = 'cpu') -> Tuple[np.ndarray, object]:
        model, hparams = _Internal.load_tacotron(model_path, device=device)
        mel = _Internal.synthesize_mel(model, text, device=device)
        waveglow = _Internal.load_waveglow(waveglow_model_path, device=device)
        audio = _Internal.waveglow_infer_to_numpy(waveglow, mel, device=device)

        return audio, hparams


def convert_to_file(text: str, model_path: str, waveglow_model_path: str, out_wav: str = 'output.wav', device: str = 'cpu'):
    """
    Convert input text into a spoken audio file using the Kimbundu and WaveGlow's models.

    This function synthesizes speech from the given text by generating a mel
    spectrogram with the Kimbundu model and converting it to waveform
    audio using WaveGlow. The resulting audio is written to a WAV file.

    Parameters
    ----------
    text : str
        The input text to be converted to speech.
    model_path : str
        Path to the Tacotron model checkpoint.
    waveglow_model_path : str
        Path to the WaveGlow model checkpoint.
    out_wav : str, optional
        Path where the output WAV file will be saved. Defaults to "output.wav".
    device : str, optional
        The device to run inference on (e.g., "cpu" or "cuda"). Defaults to "cpu".

    Returns
    -------
    str
        The path to the generated WAV file.
    """
    audio, hparams = _Internal.get_audio_hparams(model_path, waveglow_model_path, text, device=device)
    sf.write(out_wav, audio, hparams.sampling_rate)
    return out_wav



def play_default_player(text: str, model_path: str, waveglow_model_path: str, device: str = 'cpu'):
    """
    Convert input text to speech and play it using the system's default audio player.

    This function synthesizes speech from the given text using the Kimbundu model
    (via the provided checkpoint) and WaveGlow for waveform generation. The audio
    is saved temporarily to a WAV file and played immediately using the operating
    system's default audio player. The temporary file is not deleted automatically.

    Parameters
    ----------
    text : str
        The text to be converted to speech.
    model_path : str
        Path to the Tacotron model checkpoint for speech synthesis.
    waveglow_model_path : str
        Path to the WaveGlow model checkpoint for waveform generation.
    device : str, optional
        Device for model inference (e.g., "cpu" or "cuda"). Default is "cpu".
    """
    audio, hparams = _Internal.get_audio_hparams(model_path, waveglow_model_path, text, device=device)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
        out_wav = tmpfile.name
        sf.write(out_wav, audio, hparams.sampling_rate)

    if platform.system() == "Windows":
        os.system(f'start {out_wav}')
    elif platform.system() == "Darwin":  # macOS
        os.system(f'afplay "{out_wav}"')
    else:  # Linux
        os.system(f'aplay "{out_wav}"')

__all__ = [
    'convert_to_file',
    'play'
]