import os
import time
import logging
from pathlib import Path
import numpy as np
from audio_translation_pipeline import AudioTranslationPipeline
import scipy.io.wavfile as wav
import shutil

# Ensure uploads directory exists
os.makedirs('uploads', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def ensure_uploads_directory():
    """Create uploads directory if it doesn't exist."""
    Path("uploads").mkdir(exist_ok=True)
    print("Uploads directory is ready.")

def copy_audio_file(source_path):
    """Copy audio file to uploads directory."""
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source audio file not found: {source_path}")
    
    # Create uploads directory
    ensure_uploads_directory()
    
    # Get filename from path and create destination path
    filename = os.path.basename(source_path)
    dest_path = os.path.join("uploads", filename)
    
    # Copy file to uploads directory
    shutil.copy2(source_path, dest_path)
    print(f"Audio file copied to: {dest_path}")
    return dest_path

def main():
    try:
        print("Initializing pipeline with proxy support...")
        pipeline = AudioTranslationPipeline()
        print("Pipeline initialized successfully.")
        
        # Show available languages
        print("\nAvailable Languages:")
        print("-" * 30)
        languages = pipeline.get_supported_languages()
        for code, name in languages.items():
            print(f"{code}: {name}")
        
        # Example: using the Record file from current directory
        source_audio = "Record (online-voice-recorder.com) (1).mp3"
        
        try:
            # Copy audio file to uploads directory
            upload_path = copy_audio_file(source_audio)
            
            print("\nProcessing audio file...")
            print("-" * 30)
            
            # Process the audio file (example with Kannada to Hindi)
            print("\nProcessing audio with proxies...")
            print("This may take a moment as we test and rotate proxies...")
            result = pipeline.process(
                audio_file_path=upload_path,
                source_lang="kn",    # Kannada audio
                target_lang="hi"     # Translate to Hindi
            )
            
            # Print results
            print("\nTranscription and Translation Results:")
            print("-" * 50)
            print(f"Source Language: {result['source_language']}")
            print(f"Original Text: {result['original_text']}")
            print("-" * 50)
            print(f"Target Language: {result['target_language']}")
            print(f"Translated Text: {result['translated_text']}")

            try:
                # Save the generated audio
                output_filename = f"output_{int(time.time())}.wav"
                output_path = os.path.join("uploads", output_filename)
                print("\nSaving generated audio...")
                audio_array = np.array(result['audio_data'], dtype=np.float32)
                wav.write(output_path, 22050, audio_array)
                print(f"Generated audio saved to: {output_path}")
            except Exception as e:
                print(f"\nError saving audio file: {str(e)}")
            
        except FileNotFoundError as e:
            print(f"\nError: {str(e)}")
            print("Please make sure the audio file exists in the current directory.")
        
    except ValueError as e:
        print(f"\nLanguage Error: {str(e)}")
        print("Please check the available languages listed above.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("This could be due to:")
        print("1. Network connectivity issues")
        print("2. API service availability")
        print("3. Invalid audio format")
        print("Please try again or check your setup.")

if __name__ == "__main__":
    main()
