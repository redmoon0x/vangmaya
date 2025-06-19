import logging
import os
from voice_to_text import VoiceToTextConverter
from translator import TextTranslator
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioTranslationPipeline:
    def __init__(self):
        """Initialize the pipeline with voice-to-text and translator components."""
        logger.info("Initializing AudioTranslationPipeline...")
        try:
            self.voice_to_text = VoiceToTextConverter()
            self.translator = TextTranslator()
            logger.info("Pipeline components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline components: {str(e)}")
            raise
        
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages for both voice and translation."""
        # Since translator has one additional language (English), we use voice_to_text languages
        # to ensure compatibility across the pipeline
        return self.voice_to_text.get_supported_languages()
        
    def process(self, audio_file_path: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        logger.info(f"Processing audio file: {audio_file_path}")
        logger.info(f"Source language: {source_lang}, Target language: {target_lang}")
        
        """
        Process audio file through the pipeline: voice -> text -> translation
        
        Args:
            audio_file_path: Path to the audio file
            source_lang: Source language code of the audio
            target_lang: Target language code for translation
            
        Returns:
            Dictionary containing original text and translated text
            
        Raises:
            ValueError: If languages are not supported
            Exception: If processing fails
        """
        # Validate languages
        if not self.voice_to_text.is_language_supported(source_lang):
            error_msg = f"Source language {source_lang} is not supported for voice recognition"
            logger.error(error_msg)
            raise ValueError(error_msg)
        if not self.translator.is_language_supported(target_lang):
            error_msg = f"Target language {target_lang} is not supported for translation"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Step 1: Convert voice to text
        transcription_result = self.voice_to_text.transcribe(audio_file_path, source_lang)
        if not transcription_result or 'output' not in transcription_result:
            error_msg = "Voice to text conversion failed: No output in transcription result"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        try:
            original_text = transcription_result['output'][0]['source']
            logger.info(f"Successfully transcribed audio to text: {original_text[:100]}...")
        except (KeyError, IndexError) as e:
            error_msg = f"Unexpected transcription result format: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Step 2: Translate text
        try:
            translated_text = self.translator.translate(
                text=original_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            logger.info(f"Successfully translated text to {target_lang}: {translated_text[:100]}...")
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}"
            logger.error(error_msg)
            raise
        
        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "source_language": self.get_supported_languages()[source_lang],
            "target_language": self.get_supported_languages()[target_lang]
        }

if __name__ == "__main__":
    # Example usage
    pipeline = AudioTranslationPipeline()
    
    # Print supported languages
    print("Supported Languages:")
    languages = pipeline.get_supported_languages()
    for code, name in languages.items():
        print(f"{code}: {name}")
    
    # Example pipeline usage
    try:
        result = pipeline.process(
            audio_file_path="path/to/your/audio.mp3",
            source_lang="hi",  # Hindi audio
            target_lang="mr"   # Translate to Marathi
        )
        
        print("\nPipeline Results:")
        print(f"Original Text ({result['source_language']}): {result['original_text']}")
        print(f"Translated Text ({result['target_language']}): {result['translated_text']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
