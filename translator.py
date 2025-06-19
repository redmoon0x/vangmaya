from typing import Dict, List, Any
import requests
from src.request_manager import RequestManager

class TextTranslator:
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
        "doi": "Dogri",
        "en": "English"
    }
    
    def __init__(self):
        """Initialize the translator with request manager."""
        self.API_URL = 'https://admin.models.ai4bharat.org/inference/translate'
        self.request_manager = RequestManager(num_proxies=5, timeout=30)
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if the language code is supported."""
        return language_code in self.SUPPORTED_LANGUAGES

    def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (default: "en")
        
        Returns:
            Translated text
            
        Raises:
            ValueError: If language is not supported
            Exception: If translation fails
        """
        if not self.is_language_supported(target_lang):
            raise ValueError(f"Target language {target_lang} is not supported")
        if not self.is_language_supported(source_lang):
            raise ValueError(f"Source language {source_lang} is not supported")

        try:
            payload = {
                "sourceLanguage": source_lang,
                "targetLanguage": target_lang,
                "input": text,
                "task": "translation",
                "serviceId": "ai4bharat/indictrans--gpu-t4",
                "track": True
            }
            
            base_headers = {
                'Content-Type': 'application/json'
            }

            response = self.request_manager.post(
                url=self.API_URL,
                base_headers=base_headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if 'output' in result and isinstance(result['output'], list) and len(result['output']) > 0:
                return result['output'][0].get('target', '')
            raise Exception("Unexpected response format")

        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Translation failed: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages."""
        return self.SUPPORTED_LANGUAGES.copy()

if __name__ == "__main__":
    # Example usage
    translator = TextTranslator()
    print("Supported Languages:", translator.get_supported_languages())
    
    # Example translation
    text = "Hello, how are you?"
    target_lang = "hi"
    translated = translator.translate(text, target_lang=target_lang)
    print(f"Original: {text}")
    print(f"Translated to {translator.SUPPORTED_LANGUAGES[target_lang]}: {translated}")
