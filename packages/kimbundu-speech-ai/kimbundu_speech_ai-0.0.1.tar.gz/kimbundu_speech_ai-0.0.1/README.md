# kimbundu-speech-ai

**kimbundu-speech-ai** is a Python library that provides **Text-to-Speech (TTS)** and **Speech-to-Text (STT)** capabilities for **Kimbundu**, a Bantu language spoken in Angola. It allows developers, researchers, and language technology enthusiasts to build voice-enabled applications, assistive tools, and language preservation projects.

---

## Project Information

This project was developed as a **Final Year Project** for the **Informatic Engineering** degree at the **Catholic University of Angola**.

- **Institution:** Catholic University of Angola 
- **Course:** Informatic Engineering
- **Supervisor:** Engº Domingos Fernando  

---

## Features

### Text-to-Speech (TTS)

- Convert Kimbundu text into high-quality speech audio using the Kimbundu and WaveGlow models.
- Save audio to a WAV file or play it immediately on your system.

#### `convert_to_file`

```python
convert_to_file(
    text: str, 
    model_path: str, 
    waveglow_model_path: str, 
    out_wav: str = 'output.wav', 
    device: str = 'cpu'
)
````

**Description:**
Converts input text into a spoken audio file.

**Parameters:**

* `text` (str): The input text to convert.
* `model_path` (str): Path to the Kimbundu model checkpoint.
* `waveglow_model_path` (str): Path to the WaveGlow model checkpoint.
* `out_wav` (str, optional): Path to save the WAV file. Default is `'output.wav'`.
* `device` (str, optional): Device to run inference (`'cpu'` or `'cuda'`). Default is `'cpu'`.

**Returns:**

* `str`: Path to the generated WAV file.

---

#### `play_default_player`

```python
play_default_player(
    text: str, 
    model_path: str, 
    waveglow_model_path: str, 
    device: str = 'cpu'
)
```

**Description:**
Converts text to speech and plays it immediately using the system's default audio player.

**Parameters:**

* `text` (str): The text to convert to speech.
* `model_path` (str): Path to the Tacotron model checkpoint.
* `waveglow_model_path` (str): Path to the WaveGlow model checkpoint.
* `device` (str, optional): Device to run inference (`'cpu'` or `'cuda'`). Default is `'cpu'`.

---

### Speech-to-Text (STT)

* Convert Kimbundu speech audio into text using a fine-tuned Whisper model.

#### `convert_to_text`

```python
convert_to_text(
    audio_path: str, 
    model_path: str
)
```

**Description:**
Transcribes speech from an audio file into text.

**Parameters:**

* `audio_path` (str): Path to the input audio file.
* `model_path` (str): Path to the fine-tuned Kimbundu Whisper model.

**Returns:**

* `str`: The transcribed text from the audio.

---

## Installation

```bash
pip install kimbundu-speech-ai
```

**Dependencies:**

* `torch`
* `librosa`
* `soundfile`
* `numpy`
* `unidecode`
* `inflect`
* `transformers`

---

## Models

This library requires models that are downloaded separately due to their size.

#### Text-to-Speech (TTS) Models

Kimbundu TTS Model
Download:
https://drive.google.com/file/d/1iXY7beViczLIG0dEqgiBBM-1b71vzOYh/view?usp=sharing

WaveGlow Vocoder Model
Download:
https://drive.google.com/file/d/1sAnpQP3q8mOfs8rlZibh42OXiBaHzre-/view?usp=sharing

After downloading, keep note of the local paths to these files and pass them to the TTS functions as model_path and waveglow_model_path.

#### Speech-to-Text (STT) Model

Whisper Small (Kimbundu Fine-Tuned) Model
Download (ZIP file):
https://drive.google.com/file/d/15kGW4NLfeNcocNygzBOmuWASuBCPwNOx/view?usp=sharing

⚠️ Important:
After downloading the ZIP file, you must extract it.
Use the extracted folder path as the model_path argument when calling the STT function.

###### Example:

```python
STT.convert_to_text(
    audio_path="example.wav",
    model_path="path/to/extracted/whisper_small_model/"
)
```

Do not pass the ZIP file itself as the model path.

---

## Example Usage of the Library

```python
from kimbundu_speech_ai import TTS, STT

# Text-to-Speech (save to WAV)
TTS.convert_to_file(
    text="ngana nzambi",
    model_path="path/to/kimbundu model",
    waveglow_model_path="path/to/waveglow model",
    out_wav="example.wav"
)

# Speech-to-Text
transcription = STT.convert_to_text(
    audio_path="example.wav",
    model_path="path/to/kimbundu's whisper fine-tuned model"
)

print(transcription)
```

## Changelog
#### [0.0.1] – 2026-01-08
###### Added
- Initial public release.
- Text-to-Speech (TTS) support for Kimbundu using Kimbundu TTS Trained Model + WaveGlow.
- Speech-to-Text (STT) support using a fine-tuned Whisper model.
###### Notes
- Both Neural Network Models only have CPU support for their inference.