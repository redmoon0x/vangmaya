import modal
import torch
from transformers import AutoModel
import numpy as np
import soundfile as sf
import os
from pathlib import Path
import base64
import io

# Define Modal stub and container image
stub = modal.Stub("indic-tts")

# Create volume for storing reference prompts
volume = modal.Volume.persisted("prompts-volume")

# Create image with specific torch version and required packages
image = modal.Image.debian_slim().pip_install(
    "torch==2.7.1",
    "transformers>=4.30.0",
    "accelerate>=0.20.0",
    "sentencepiece>=0.1.99",
    "safetensors>=0.3.1",
    "soundfile>=0.11.0",
    "numpy>=1.20.0",
    "git+https://github.com/ai4bharat/IndicF5.git"
)

# Define Modal class with GPU support
@stub.cls(
    image=image,
    gpu=modal.gpu.T4(),
    secret=modal.Secret.from_name("huggingface-token"),
    volumes={"/prompts": volume}
)
class IndicTTS:
    def __init__(self):
        # Load model using HF token for authentication
        self.hf_token = os.environ["HUGGINGFACE_TOKEN"]
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize model
        self.model = AutoModel.from_pretrained(
            "ai4bharat/IndicF5",
            use_auth_token=self.hf_token,
            trust_remote_code=True
        ).to(self.device)

    @modal.method()
    def generate_speech(
        self,
        text: str,
        ref_audio_base64: str = None,
        ref_text: str = None
    ) -> bytes:
        """
        Generate speech from text using IndicF5
        Args:
            text: Input text to convert to speech
            ref_audio_base64: Base64 encoded reference audio file (WAV format)
            ref_text: Text corresponding to reference audio
        Returns:
            bytes: Audio data in WAV format
        """
        try:
            # If reference audio is provided, save it temporarily
            if ref_audio_base64 and ref_text:
                ref_audio_data = base64.b64decode(ref_audio_base64)
                ref_audio_path = "/prompts/ref_audio.wav"
                with open(ref_audio_path, "wb") as f:
                    f.write(ref_audio_data)
            else:
                # Use default reference prompt
                ref_audio_path = "/prompts/PAN_F_HAPPY_00001.wav"
                ref_text = "ਭਹੰਪੀ ਵਿੱਚ ਸਮਾਰਕਾਂ ਦੇ ਭਵਨ ਨਿਰਮਾਣ ਕਲਾ ਦੇ ਵੇਰਵੇ ਗੁੰਝਲਦਾਰ ਅਤੇ ਹੈਰਾਨ ਕਰਨ ਵਾਲੇ ਹਨ, ਜੋ ਮੈਨੂੰ ਖੁਸ਼ ਕਰਦੇ  ਹਨ।"

            # Generate speech
            audio = self.model(
                text,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text
            )

            # Normalize audio
            if audio.dtype == np.int16:
                audio = audio.astype(np.float32) / 32768.0

            # Save to bytes buffer
            buffer = io.BytesIO()
            sf.write(buffer, np.array(audio, dtype=np.float32), samplerate=24000, format='WAV')
            buffer.seek(0)
            
            return buffer.read()
            
        except Exception as e:
            raise modal.Error(f"Speech generation failed: {str(e)}")

# Create FastAPI endpoint
@stub.function()
@modal.web_endpoint(method="POST")
async def tts_endpoint(
    text: str,
    ref_audio_base64: str = None,
    ref_text: str = None
):
    """
    Web endpoint for text-to-speech conversion
    Args:
        text: Input text to convert to speech
        ref_audio_base64: Base64 encoded reference audio file (optional)
        ref_text: Text corresponding to reference audio (optional)
    Returns:
        Audio file in WAV format
    """
    tts = IndicTTS()
    audio_data = tts.generate_speech.call(text, ref_audio_base64, ref_text)
    
    return modal.Response(
        audio_data,
        headers={
            "Content-Type": "audio/wav",
            "Content-Disposition": "attachment; filename=speech.wav"
        }
    )

# For local testing
if __name__ == "__main__":
    stub.serve()
