import os
import sys
from typing import Optional, Tuple

import numpy as np
import torch
import soundfile as sf

# Ensure the package directory is on sys.path so the repo's modules can be imported
pkg_dir = os.path.dirname(__file__)
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

from kimbundu_speech_ai.hparams import create_hparams
from kimbundu_speech_ai.model import Tacotron2
from kimbundu_speech_ai.text import text_to_sequence

ROOT = r"C:\Users\rsabino\Documents\projecto final\kutanga\backend"
# CKPT_DIR = os.path.join(ROOT, "kimbundu_tts", "newoutdir")
# WAVEGLOW = os.path.join(ROOT, "kimbundu_tts", "waveglow.pt")


def find_latest_checkpoint(outdir: str) -> Optional[str]:
    if not os.path.isdir(outdir):
        return None
    checkpoints = [f for f in os.listdir(outdir) if f.startswith("checkpoint_")]
    if not checkpoints:
        return None
    latest_ckpt = sorted(checkpoints, key=lambda x: int(x.split('_')[-1]))[-1]
    return os.path.join(outdir, latest_ckpt)

# ckpt = find_latest_checkpoint(CKPT_DIR)


def load_tacotron(checkpoint_path: str, hparams_overrides: Optional[str] = None, device: str = 'cpu') -> Tuple[Tacotron2, object]:
    hparams = create_hparams(hparams_overrides or "sampling_rate=22050")
    model = Tacotron2(hparams)
    state = torch.load(checkpoint_path, map_location=device)
    if 'state_dict' in state:
        model.load_state_dict(state['state_dict'])
    else:
        model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model, hparams


def synthesize_mel(model: Tacotron2, text: str, hparams, cleaners: list = ['english_cleaners'], device: str = 'cpu') -> torch.Tensor:
    sequence = np.array(text_to_sequence(text, cleaners))[None, :]
    sequence = torch.from_numpy(sequence).long().to(device)
    with torch.no_grad():
        mel_outputs, mel_outputs_postnet, _, _ = model.inference(sequence)
    mel = mel_outputs_postnet[0].unsqueeze(0).cpu()
    return mel


def _maybe_resolve_waveglow_path(path: str) -> str:
    if os.path.isdir(path):
        candidate = os.path.join(path, 'waveglow.pt')
        if os.path.exists(candidate):
            return candidate
    return path


def load_waveglow(waveglow_path: str, device: str = 'cpu'):
    waveglow_path = _maybe_resolve_waveglow_path(waveglow_path)
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
                state = torch.load(waveglow_path, map_location=device, weights_only=False)
        elif hasattr(ser, 'add_safe_globals') and allowed_globals:
            ser.add_safe_globals(allowed_globals)
            state = torch.load(waveglow_path, map_location=device)
        else:
            # Fallback: try full load (may raise on newer torch versions)
            state = torch.load(waveglow_path, map_location=device)
    except TypeError:
        # Older torch that doesn't accept weights_only arg
        state = torch.load(waveglow_path, map_location=device)
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


def to_file(text: str, checkpoint_path: str, waveglow_path: str, out_wav: str = 'output.wav', device: str = 'cpu', hparams_overrides: Optional[str] = None, cleaners: list = ['english_cleaners']):
    model, hparams = load_tacotron(checkpoint_path, hparams_overrides=hparams_overrides, device=device)
    mel = synthesize_mel(model, text, hparams, cleaners=cleaners, device=device)
    waveglow = load_waveglow(waveglow_path, device=device)
    audio = waveglow_infer_to_numpy(waveglow, mel, device=device)
    sf.write(out_wav, audio, hparams.sampling_rate)
    return out_wav


__all__ = [
    'find_latest_checkpoint', 'load_tacotron', 'synthesize_mel', 'load_waveglow', 'waveglow_infer_to_numpy', 'to_file'
]
