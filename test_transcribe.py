import json
from voice_to_text import VoiceToTextConverter
from translator import TextTranslator
from text_to_speech import TextToSpeech

def main():
    try:
        # Initialize the converter
        converter = VoiceToTextConverter()
        
        # Print supported languages
        print("\nSupported Languages:")
        for code, language in converter.get_supported_languages().items():
            print(f"{code}: {language}")
        
        # Test transcription
        print("\nTranscribing audio file...")
        result = converter.transcribe('Record (online-voice-recorder.com).mp3', 'hi')  # Using Kannada as source language
        
        print("\nTranscription Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Step 3: Translate the transcribed text
        print("\nTranslating to Hindi...")
        translator = TextTranslator()
        source_text = result['output'][0]['source']
        translation = translator.translate(source_text, "kn")  # Using 'hi' for Hindi
        print("\nTranslation Result:")
        print("Translated text:", translation)

        # Step 4: Convert translated text to speech using original voice
        print("\nSynthesizing speech...")
        tts = TextToSpeech()
        audio_path = 'Record (online-voice-recorder.com).mp3'
        synthesized = tts.synthesize(
            translated_text=translation,
            reference_audio_path=audio_path,
            reference_text=source_text
        )
        
        # Save the synthesized audio
        output_path = "output_audio.wav"
        with open(output_path, "wb") as f:
            f.write(synthesized)
        print(f"\nSynthesized speech saved to: {output_path}")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
