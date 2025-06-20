import logging
import json
import numpy as np
import soundfile as sf
import base64
import io
import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self, api_url: str = None, sample_rate: int = 24000):
        """
        Initialize text to speech converter.
        
        Args:
            api_url: URL of the Modal TTS API endpoint
            sample_rate: Output audio sample rate (default: 24000)
        """
        self.api_url = api_url or os.getenv("TTS_API_URL")
        if not self.api_url:
            raise ValueError("API URL must be provided either in constructor or as TTS_API_URL environment variable")
        # Ensure API URL doesn't end with slash
        self.api_url = self.api_url.rstrip('/')
        self.sample_rate = sample_rate
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods={"POST", "GET"}
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        
        logger.info(f"Initializing TextToSpeech with API URL: {self.api_url}, sample rate: {self.sample_rate}")

    def generate_speech(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        output_path: str = None
    ) -> dict:
        """
        Generate speech using text and reference audio through Modal API.

        Args:
            text: Text to convert to speech
            ref_audio_path: Path to reference audio file
            ref_text: Transcribed text from reference audio
            output_path: Optional path to save the output audio file

        Returns:
            Dictionary containing:
                - file_path: Path to saved audio file
                - base64_audio: Base64 encoded audio data
                - sample_rate: Audio sample rate
        """
        if output_path is None:
            output_path = "output.wav"

        max_retries = 3
        retry_count = 0
        last_error = None

        # Read audio file once and keep the content
        with open(ref_audio_path, 'rb') as f:
            audio_content = f.read()

        while retry_count < max_retries:
            try:
                logger.info("Generating speech with reference audio...")
                logger.info(f"Input text: {text}")
                logger.info(f"Reference text: {ref_text}")
                logger.info(f"Reference audio path: {ref_audio_path}")

                # Create file-like object from audio content
                audio_file = io.BytesIO(audio_content)
                audio_file.name = 'reference.wav'

                # Prepare multipart/form-data request
                files = {
                    'ref_audio': ('reference.wav', audio_file, 'audio/wav')
                }
                data = {
                    'text': text,
                    'ref_text': ref_text
                }

                # Make API request with timeout
                logger.info("Sending request to Modal API...")
                response = self.session.post(
                    f"{self.api_url}/synthesize",
                    files=files,
                    data=data,
                    timeout=60
                )

                if response.status_code != 200:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                # Get audio data from response
                audio_data = response.content

                try:
                    # Convert to numpy array for processing
                    audio_buffer = io.BytesIO(audio_data)
                    audio, _ = sf.read(audio_buffer)

                    # Check for silent or low amplitude audio
                    max_abs = np.max(np.abs(audio))
                    if max_abs < 0.01:
                        logger.warning(f"Audio amplitude is very low: {max_abs}. Amplifying...")
                        if max_abs == 0:
                            logger.warning("Audio is completely silent. Adding noise carrier...")
                            audio = np.sin(np.linspace(0, 100, len(audio)) * 2 * np.pi)
                            audio = audio * 0.1
                        else:
                            audio = audio * (0.1 / max_abs)

                    # Ensure audio is float32
                    audio = np.array(audio, dtype=np.float32)

                    # Save the audio file
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    logger.info(f"Writing audio: shape={audio.shape}, min={np.min(audio):.4f}, max={np.max(audio):.4f}, mean={np.mean(audio):.4f}")
                    
                    sf.write(
                        str(output_path),
                        audio,
                        samplerate=self.sample_rate
                    )

                    # Create base64 encoded version
                    audio_bytes = io.BytesIO()
                    sf.write(audio_bytes, audio, samplerate=self.sample_rate, format='WAV')
                    audio_bytes.seek(0)
                    base64_audio = base64.b64encode(audio_bytes.read()).decode('utf-8')

                    logger.info(f"Audio saved to: {output_path}")
                    return {
                        'file_path': str(output_path),
                        'base64_audio': base64_audio,
                        'sample_rate': self.sample_rate
                    }

                except Exception as e:
                    logger.error(f"Error processing audio: {str(e)}")
                    # Save raw response content as fallback
                    output_path.write_bytes(audio_data)
                    base64_audio = base64.b64encode(audio_data).decode('utf-8')
                    
                    return {
                        'file_path': str(output_path),
                        'base64_audio': base64_audio,
                        'sample_rate': self.sample_rate
                    }

            except Exception as e:
                retry_count += 1
                last_error = str(e)
                if retry_count < max_retries:
                    wait_time = retry_count * 2
                    logger.warning(f"Attempt {retry_count} failed: {last_error}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    error_msg = f"Speech generation failed after {max_retries} attempts. Last error: {last_error}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage with Hindi text
    api_url = os.getenv("TTS_API_URL", "https://your-modal-endpoint.modal.run")
    text = "नमस्ते! कैसे हैं आप?"
    ref_text = "Hello, how are you?"
    ref_audio_path = "test_audio.wav"
    output_path = "output.wav"
    
    # Convert text to speech
    converter = TextToSpeech(api_url=api_url)
    try:
        result = converter.generate_speech(
            text=text,
            ref_audio_path=ref_audio_path,
            ref_text=ref_text,
            output_path=output_path
        )
        logger.info(f"Text-to-speech conversion completed. Audio saved to: {result['file_path']}")
        logger.info(f"Base64 audio available (length: {len(result['base64_audio'])}, sample rate: {result['sample_rate']})")
        
        # Optionally write base64 to file for testing
        with open("output_base64.txt", "w") as f:
            f.write(result['base64_audio'])
    except Exception as e:
        logger.error(f"Text-to-speech conversion failed: {e}")
