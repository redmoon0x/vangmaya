from anuvaad_rev import IndicTranslator
from typing import Dict, List, Any

class TextTranslator:
    def __init__(self):
        """Initialize the translator with IndicTranslator."""
        self.translator = IndicTranslator()
    
    def translate(self, text: str, target_lang: str) -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        return self.translator.translate(text, target_lang=target_lang)
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages."""
        return self.translator.get_supported_languages()
