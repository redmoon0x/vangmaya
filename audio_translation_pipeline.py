import logging
import os
import shutil
import base64
from typing import Dict, Any
from pathlib import Path
from voice_to_text import VoiceToTextConverter
from translator import TextTranslator
from text_to_speech import TextToSpeech

logger = logging.getLogger(__name__)

class AudioTranslationPipeline:
    def __init__(self):
        """Initialize pipeline components."""
        logger.info("Initializing AudioTranslationPipeline...")
        try:
            self.transcriber = VoiceToTextConverter()
            self.translator = TextTranslator()
            # Initialize TTS with API URL
            api_url = os.environ.get("TTS_API_URL")
            self.synthesizer = TextToSpeech(api_url=api_url)
            logger.info("Pipeline components initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize pipeline components: " + str(e))
            raise

    def process(
        self,
        audio_file_path: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Process audio through the complete pipeline.
        
        Args:
            audio_file_path: Path to input audio file
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dict containing original text, translated text, and generated audio
        """
        logger.info(f"Processing audio file: {audio_file_path}")
        logger.info(f"Source language: {source_lang}, Target language: {target_lang}")

        try:
            # Step 1: Transcribe audio to text
            transcription = self.transcriber.transcribe(
                audio_file_path=audio_file_path,
                source_language=source_lang
            )
            original_text = transcription.get("output", [{}])[0].get("source", "")
            logger.info(f"Successfully transcribed audio to text: {original_text}")

            # Step 2: Translate text
            translated_text = self.translator.translate(
                text=original_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            logger.info(f"Successfully translated text to {target_lang}: {translated_text}")

            # Step 3: Generate speech in target language
            logger.info(f"Generating speech using IndicF5 model...")
            
            # Create a unique output filename based on timestamp
            import time
            output_filename = f"output_{int(time.time())}.wav"
            output_path = os.path.join("outputs", output_filename)
            os.makedirs("outputs", exist_ok=True)
            
            # Generate the speech with fixed sample rate of 24000 Hz to match reference code
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    tts_result = self.synthesizer.generate_speech(
                        text=translated_text,
                        ref_audio_path=audio_file_path,  # Use input audio as reference
                        ref_text=original_text,  # Use transcribed text as reference text
                        output_path=output_path
                    )
                    logger.info(f"Speech generated successfully: {tts_result['file_path']}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Speech generation attempt {retry_count} failed: {str(e)}. Retrying...")
                        # Wait a moment before retrying
                        import time
                        time.sleep(1)
                    else:
                        logger.error(f"All speech generation attempts failed after {max_retries} retries")
                        raise

            return {
                'source_language': source_lang,
                'target_language': target_lang,
                'original_text': original_text,
                'translated_text': translated_text,
                'audio_path': tts_result['file_path'],
                'audio_data': tts_result['file_path'],  # For backward compatibility with file paths
                'base64_audio': tts_result['base64_audio'],  # Base64 encoded audio
                'sample_rate': tts_result['sample_rate']  # Sample rate information
            }

        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            raise

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages."""
        return self.translator.get_supported_languages()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    pipeline = AudioTranslationPipeline()
    print("Supported Languages:")
    print("-" * 30)
    languages = pipeline.get_supported_languages()
    for code, name in languages.items():
        print(f"{code}: {name}")
