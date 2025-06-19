# IndicF5 TTS Modal Deployment

This repository contains the code to deploy the IndicF5 text-to-speech model on Modal.

## Setup and Deployment

1. Install Modal CLI:
```bash
pip install modal-client
```

2. Login to Modal:
```bash
modal token new
```

3. Deploy the model:
```bash
modal deploy modal_deploy.py
```

## Usage Example

```python
from modal import Stub

# Connect to the deployed endpoint
stub = Stub("indicf5-tts")

# Generate speech
audio_data = stub.IndicF5.generate_speech.remote(
    text="नमस्ते! संगीत की तरह जीवन भी खूबसूरत होता है।",
    ref_audio_path="path/to/reference.wav",  # You'll need to provide a reference audio
    ref_text="Reference audio transcript"     # Transcript of the reference audio
)

# Save the generated audio
import numpy as np
import soundfile as sf

audio_array = np.array(audio_data, dtype=np.float32)
sf.write("output.wav", audio_array, samplerate=24000)
```

## Important Notes

1. Make sure you have a Modal account (sign up at modal.com if you don't)
2. The model requires a reference audio file and its transcript for speech generation
3. The deployed endpoint accepts text input in Indic languages
4. The generated audio is returned as a normalized float32 array

## Model Details

IndicF5 is a text-to-speech model that supports multiple Indic languages. It uses a reference audio approach to match the speaker characteristics and prosody of the input reference audio.
