import requests

response = requests.post(
    "https://deviprasadshetty400--indicf5-tts-generate-speech.modal.run",
    json={
        "text": "नमस्ते! संगीत की तरह जीवन भी खूबसूरत होता है।",
        "ref_audio_path": "path/to/reference.wav",
        "ref_text": "Reference audio transcript"
    }
)

# The response will contain the generated audio as a list of float values
audio_data = response.json()
