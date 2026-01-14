import os
import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class _Internal:
    @staticmethod
    def load_model_processor(model_path: str):
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Checkpoint path does not exist: {model_path}")
            else:
                processor = WhisperProcessor.from_pretrained(model_path)
                model = WhisperForConditionalGeneration.from_pretrained(model_path)
                return model, processor
        except Exception as e:
            raise Exception(f"Failed to load model from {model_path}: {str(e)}")


def convert_to_text(audio_path: str, model_path: str):
    """
    Transcribe speech from an audio file into text using a Whisper-based model.

    This function loads an audio file, processes it through a fine-tuned speech 
    recognition model (Whisper), and returns the corresponding text transcription.

    Parameters
    ----------
    audio_path : str
        Path to the input audio file. 
    model_path : str
        Path to the fine-tuned Kimbundu Whisper model.

    Returns
    -------
    str
        The transcribed text from the audio.
    """
    audio, sr = librosa.load(audio_path, sr=16000)
    model, processor = _Internal.load_model_processor(model_path)

    # Process audio with Whisper processor
    inputs = processor(
            audio, 
            sampling_rate=16000, 
            return_tensors="pt",
            padding=True
    )
        
        # Generate transcription
    with torch.no_grad():
        predicted_ids = model.generate(inputs.input_features)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        return transcription.strip()
    

__all__ = [
    'convert_to_text'
]