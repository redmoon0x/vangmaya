from gradio_client import Client, handle_file
from typing import Any

class TextToSpeech:
    def __init__(self):
        """Initialize the TTS with IndicF5 model."""
        self.client = Client("ai4bharat/IndicF5")
    
    def synthesize(self, translated_text: str, reference_audio_path: str, reference_text: str) -> Any:
        """
        Synthesize speech from text using reference audio's voice.
        
        Args:
            translated_text: The text to convert to speech
            reference_audio_path: Path to the reference audio file
            reference_text: The transcribed text from reference audio
            
        Returns:
            Synthesized speech data
        """
        # Get the audio file path from the API
        result = self.client.predict(
            text=translated_text,
            ref_audio=handle_file(reference_audio_path),
            ref_text=reference_text,
            api_name="/synthesize_speech"
        )
        
        # Read the generated audio file and return its bytes
        if isinstance(result, str):
            with open(result, 'rb') as f:
                return f.read()
        return result
