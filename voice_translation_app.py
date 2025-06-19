import gradio as gr
import requests
import json
import tempfile
import os
import numpy as np
from scipy.io import wavfile
import soundfile as sf
from voice_to_text import VoiceToTextConverter
from translator import TextTranslator

class VoiceTranslationPipeline:
    def __init__(self):
        self.voice_to_text = VoiceToTextConverter()
        self.translator = TextTranslator()
        self.tts_url = "https://deviprasadshetty400--indicf5-tts-generate-speech.modal.run"

    def generate_speech(self, text, ref_audio_path, ref_text):
        response = requests.post(
            self.tts_url,
            json={
                "text": text,
                "ref_audio_path": ref_audio_path,
                "ref_text": ref_text
            }
        )
        return response.json()

    def process(self, audio_path, source_lang, target_lang):
        try:
            # Step 1: Convert voice to text
            transcription_result = self.voice_to_text.transcribe(audio_path, source_lang)
            transcribed_text = transcription_result.get('output', [{}])[0].get('source', '')
            
            if not transcribed_text:
                raise Exception("Failed to transcribe audio")

            # Step 2: Translate text
            translated_text = self.translator.translate(
                transcribed_text, 
                target_lang=target_lang,
                source_lang=source_lang
            )

            if not translated_text:
                raise Exception("Failed to translate text")

            # Step 3: Generate speech from translated text
            speech_data = self.generate_speech(
                text=translated_text,
                ref_audio_path=audio_path,
                ref_text=transcribed_text
            )

            # Save and validate the audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_path = temp_file.name
                
                try:
                    # Convert the response to numpy array
                    audio_array = np.array(speech_data)
                    
                    # Normalize the audio to [-1, 1] range
                    audio_array = audio_array / np.max(np.abs(audio_array))
                    
                    # Save using soundfile which handles float32 format better
                    sf.write(audio_path, audio_array, 16000, subtype='PCM_16')
                    
                    # Verify the file was written correctly
                    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                        raise Exception("Failed to generate audio file")
                        
                except (ValueError, TypeError) as e:
                    raise Exception(f"Invalid audio data received from TTS service: {str(e)}")
                except Exception as e:
                    raise Exception(f"Error processing audio data: {str(e)}")

            return {
                "transcribed_text": transcribed_text,
                "translated_text": translated_text,
                "output_audio": audio_path
            }

        except Exception as e:
            raise Exception(f"Pipeline error: {str(e)}")

def create_interface():
    pipeline = VoiceTranslationPipeline()

    # Get supported languages for dropdowns
    supported_langs = pipeline.voice_to_text.get_supported_languages()
    lang_choices = [(code, name) for code, name in supported_langs.items()]
    target_lang_choices = [
        (code, name) for code, name in supported_langs.items()
        if name in [
            "Assamese", "Bengali", "Gujarati", "Hindi", 
            "Kannada", "Malayalam", "Marathi", "Odia",
            "Punjabi", "Tamil", "Telugu"
        ]
    ]

    def process_audio(audio_path, source_lang, target_lang):
        try:
            result = pipeline.process(audio_path, source_lang, target_lang)
            return (
                result["transcribed_text"],
                result["translated_text"],
                result["output_audio"]
            )
        except Exception as e:
            return f"Error: {str(e)}", "", None

    interface = gr.Interface(
        fn=process_audio,
        inputs=[
            gr.Audio(source="microphone", type="filepath", label="Voice Input"),
            gr.Dropdown(choices=lang_choices, value="en", label="Source Language"),
            gr.Dropdown(choices=target_lang_choices, value="hi", label="Target Language")
        ],
        outputs=[
            gr.Textbox(label="Transcribed Text"),
            gr.Textbox(label="Translated Text"),
            gr.Audio(label="Generated Speech")
        ],
        title="Voice Translation Pipeline",
        description=(
            "Record or upload voice, select source and target languages, "
            "and get translated speech output. Supported target languages include: "
            "Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, "
            "Odia, Punjabi, Tamil, and Telugu."
        )
    )
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
