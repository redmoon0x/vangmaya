import base64
import requests
from typing import Dict, Any
import json

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

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://ai4bharat.iitm.ac.in',
                'Referer': 'https://ai4bharat.iitm.ac.in/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
            }

            response = requests.post(self.API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

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
