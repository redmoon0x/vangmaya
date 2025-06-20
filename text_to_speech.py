import logging
import os
import base64
import shutil
from pathlib import Path
from gradio_client import Client, handle_file
from src.request_manager import RequestManager

logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self):
        """Initialize text to speech converter using Hugging Face hosted Gradio space."""
        self._client = None
        self.request_manager = RequestManager()

    def generate_speech(self, text: str, ref_audio_path: str, ref_text: str, output_path: str = None) -> dict:
        """
        Generate speech using text and reference audio.

        Args:
            text: Text to convert to speech (translated text)
            ref_audio_path: Path to reference audio file
            ref_text: Text from reference audio (transcribed text)
            output_path: Optional path to save the output audio file

        Returns:
            Dictionary containing:
                - file_path: Path to saved audio file
        """
        if output_path is None:
            output_path = "output.wav"

        try:
            logger.info("Generating speech...")
            
            # Initialize HF space client
            if self._client is None:
                self._client = Client("ai4bharat/IndicF5")

            # Handle reference audio file through ScraperAPI if it's a URL
            if ref_audio_path.startswith(('http://', 'https://')):
                logger.info("Downloading reference audio through ScraperAPI...")
                with Path("temp_ref.wav").open("wb") as f:
                    response = self.request_manager.session.get(ref_audio_path)
                    response.raise_for_status()
                    f.write(response.content)
                ref_file = "temp_ref.wav"
            else:
                ref_file = ref_audio_path

            try:
                # Make prediction using reference audio
                result = self._client.predict(
                    text=text,                    # Translated text
                    ref_audio=handle_file(ref_file),  # Input audio
                    ref_text=ref_text,            # Transcribed text
                    api_name="/synthesize_speech"
                )
            finally:
                # Clean up temp file if we created one
                if ref_audio_path.startswith(('http://', 'https://')):
                    try:
                        os.remove("temp_ref.wav")
                    except:
                        pass

            # Save result to output path
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(result, str) and os.path.exists(result):
                # Copy the file first, then remove original to work across drives
                shutil.copy2(result, str(output_path))
                try:
                    os.remove(result)  # Clean up the temp file
                except:
                    pass  # Ignore cleanup errors
                logger.info(f"Audio saved to: {output_path}")
                return {'file_path': str(output_path)}
            else:
                raise Exception("Failed to get valid output from TTS service")

        except Exception as e:
            error_msg = str(e)
            if "Proxy Authentication Required" in error_msg:
                raise RuntimeError("ScraperAPI authentication failed. Check your SCRAPER_API_KEY environment variable.")
            elif "Connection refused" in error_msg:
                raise RuntimeError("Failed to connect. Check your network connection.")
            else:
                raise RuntimeError(f"TTS generation failed: {error_msg}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    text = "Hello! This is translated text"  # This would be the translated text
    ref_text = "Hello! This is original text"  # This would be transcribed text
    ref_audio_path = "test.wav"  # This would be input audio
    
    try:
        converter = TextToSpeech()
        result = converter.generate_speech(
            text=text,
            ref_audio_path=ref_audio_path,
            ref_text=ref_text,
            output_path="output.wav"
        )
        print(f"Generated audio saved to: {result['file_path']}")
    except Exception as e:
        print(f"Error: {e}")
