import base64
import requests
import json
from typing import Dict, Any
from src.request_manager import RequestManager

class VoiceToTextConverter:
    SUPPORTED_LANGUAGES = {
        "mr": "Marathi",
        "gu": "Gujarati",
        "or": "Odia",
        "brx": "Bodo",
        "ml": "Malayalam",
        "kok": "Konkani",
        "ks": "Kashmiri",
        "sd": "Sindhi",
        "bn": "Bengali",
        "sat": "Santali",
        "ta": "Tamil",
        "mai": "Maithili",
        "ne": "Nepali",
        "pa": "Punjabi",
        "te": "Telugu",
        "mni": "Meitei (Manipuri)",
        "ur": "Urdu",
        "kn": "Kannada",
        "as": "Assamese",
        "sa": "Sanskrit",
        "hi": "Hindi",
        "doi": "Dogri"
    }

    def __init__(self):
        self.API_URL = 'https://admin.models.ai4bharat.org/inference/transcribe'
        # Initialize request manager with settings optimized for large audio uploads
        self.request_manager = RequestManager(
            num_proxies=5,             # Larger pool for audio uploads
            timeout=30,                # Longer timeout for audio processing
            max_requests_per_proxy=10  # More frequent rotation for stability
        )
        # Initialize empty cache for frequently used audio
        self.result_cache = {}

    def is_language_supported(self, language_code: str) -> bool:
        """Check if the language code is supported."""
        return language_code in self.SUPPORTED_LANGUAGES

    def convert_audio_to_base64(self, audio_file_path: str) -> str:
        """Convert audio file to base64 string."""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                return base64.b64encode(audio_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error reading audio file: {str(e)}")

    def transcribe(self, audio_file_path: str, source_language: str) -> Dict[str, Any]:
        """Transcribe audio file to text."""
        if not self.is_language_supported(source_language):
            raise ValueError(f"Language {source_language} is not supported")

        # Check cache first
        cache_key = f"{audio_file_path}:{source_language}"
        if cache_key in self.result_cache:
            return self.result_cache[cache_key]

        try:
            audio_content = self.convert_audio_to_base64(audio_file_path)

            payload = {
                "audioContent": audio_content,
                "sourceLanguage": source_language,
                "domain": "general",
                "samplingRate": 16000,
                "serviceId": "ai4bharat/conformer-multilingual-all--gpu-t4",
                "task": "asr",
                "track": True,
                "preProcessors": [],
                "postProcessors": []
            }

            # Headers optimized for audio upload
            base_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Connection': 'keep-alive'
            }

            response = self.request_manager.post(
                url=self.API_URL,
                base_headers=base_headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            # Cache successful results
            self.result_cache[cache_key] = result
            
            return result

        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Transcription failed: {str(e)}")

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages."""
        return self.SUPPORTED_LANGUAGES.copy()

if __name__ == "__main__":
    # Example usage
    converter = VoiceToTextConverter()
    print("Supported Languages:", converter.get_supported_languages())
