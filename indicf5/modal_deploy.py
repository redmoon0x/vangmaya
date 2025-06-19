import modal
from modal import Image, fastapi_endpoint

# Define the Modal app
app = modal.App("indicf5-tts")

# Create a container image with the required dependencies
image = (
    Image.debian_slim()
    .apt_install("git")
    .pip_install(
        "torch",
        "transformers",
        "soundfile",
        "numpy",
        "fastapi[standard]",  # Added FastAPI with recommended extensions
        "git+https://github.com/ai4bharat/IndicF5.git"
    )
)

@app.function(
    image=image,
    gpu="T4",  # Use T4 GPU for inference
    timeout=600  # 10 minute timeout
)
@fastapi_endpoint()
def generate_speech(text: str, ref_audio_path: str, ref_text: str):
    from transformers import AutoModel
    import numpy as np
    
    # Load model
    model = AutoModel.from_pretrained(
        "ai4bharat/IndicF5",
        trust_remote_code=True
    )
    
    # Generate speech
    audio = model(
        text,
        ref_audio_path=ref_audio_path,
        ref_text=ref_text
    )

    # Normalize audio if needed
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0

    return audio.tolist()  # Convert to list for JSON serialization

if __name__ == "__main__":
    app.serve()
