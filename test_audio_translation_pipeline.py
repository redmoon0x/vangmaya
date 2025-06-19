import unittest
from audio_translation_pipeline import AudioTranslationPipeline
from pathlib import Path
import os

class TestAudioTranslationPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = AudioTranslationPipeline()
        # Create uploads directory if it doesn't exist
        Path("uploads").mkdir(exist_ok=True)
        
    def test_supported_languages(self):
        """Test that supported languages are available."""
        languages = self.pipeline.get_supported_languages()
        self.assertIsInstance(languages, dict)
        self.assertGreater(len(languages), 0)
        self.assertTrue("hi" in languages)  # Hindi should be supported
        
    def test_invalid_source_language(self):
        """Test error handling for invalid source language."""
        with self.assertRaises(ValueError) as context:
            self.pipeline.process(
                audio_file_path="uploads/test.mp3",
                source_lang="invalid",
                target_lang="hi"
            )
        self.assertTrue("not supported" in str(context.exception))
        
    def test_invalid_target_language(self):
        """Test error handling for invalid target language."""
        with self.assertRaises(ValueError) as context:
            self.pipeline.process(
                audio_file_path="uploads/test.mp3",
                source_lang="hi",
                target_lang="invalid"
            )
        self.assertTrue("not supported" in str(context.exception))
        
    def test_nonexistent_audio_file(self):
        """Test error handling for nonexistent audio file."""
        with self.assertRaises(Exception):
            self.pipeline.process(
                audio_file_path="uploads/nonexistent.mp3",
                source_lang="hi",
                target_lang="mr"
            )

if __name__ == "__main__":
    unittest.main()
