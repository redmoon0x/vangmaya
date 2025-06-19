import gradio as gr
import os
from voice_to_text import VoiceToTextConverter
from translator import TextTranslator
from text_to_speech import TextToSpeech

class VoxLingo:
    def __init__(self):
        self.converter = VoiceToTextConverter()
        self.translator = TextTranslator()
        self.tts = TextToSpeech()
        self.supported_languages = self.converter.get_supported_languages()
    
    def process_audio(self, audio, source_lang, target_lang):
        """Process audio through the complete pipeline."""
        if audio is None:
            raise gr.Error("Please provide an audio input!")

        try:
            # Save the input audio temporarily
            temp_input = "temp_input.wav"
            
            # Handle different audio input types
            if isinstance(audio, (str, os.PathLike)):  # File path
                if not os.path.exists(audio):
                    raise gr.Error("Audio file not found")
                import shutil
                shutil.copy2(audio, temp_input)
            elif isinstance(audio, tuple) and len(audio) == 2:  # Microphone recording
                sample_rate, audio_data = audio
                import scipy.io.wavfile as wavfile
                wavfile.write(temp_input, sample_rate, audio_data)
            elif isinstance(audio, dict) and 'name' in audio:  # Gradio file upload
                import shutil
                shutil.copy2(audio['name'], temp_input)
            else:
                raise gr.Error("Invalid audio input. Please record or upload an audio file.")
            
            # Step 1: Transcribe
            result = self.converter.transcribe(temp_input, source_lang)
            source_text = result['output'][0]['source']
            
            # Step 2: Translate
            translated_text = self.translator.translate(source_text, target_lang)
            
            # Step 3: Synthesize speech
            synthesized = self.tts.synthesize(
                translated_text=translated_text,
                reference_audio_path=temp_input,
                reference_text=source_text
            )
            
            # Save the output
            output_path = "output_audio.wav"
            with open(output_path, "wb") as f:
                f.write(synthesized)
            
            # Cleanup
            if os.path.exists(temp_input):
                os.remove(temp_input)
            
            return source_text, translated_text, output_path
        
        except Exception as e:
            raise gr.Error(f"Error: {str(e)}")

    def create_interface(self):
        """Create the Gradio interface."""
        language_choices = [(v, k) for k, v in self.supported_languages.items()]
        
        with gr.Blocks(title="VoxLingo - Voice Language Translator") as interface:
            gr.Markdown("""
            # 🎙️ VoxLingo - Speak in Any Indian Language
            Upload or record audio in one language and get it translated to another language while preserving the original voice!
            """)
            
            with gr.Row():
                source_lang = gr.Dropdown(
                    choices=language_choices,
                    label="Source Language",
                    value=language_choices[0][1]
                )
                target_lang = gr.Dropdown(
                    choices=language_choices,
                    label="Target Language",
                    value=language_choices[0][1]
                )
            
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(
                        sources=["microphone", "upload"],
                        type="filepath",
                        label="Input Audio"
                    )
                    transcription = gr.Textbox(label="Transcribed Text")
                    translation = gr.Textbox(label="Translated Text")
                with gr.Column():
                    output_audio = gr.Audio(label="Translated Audio")
            
            with gr.Row():
                submit_btn = gr.Button("🔄 Translate", variant="primary")
                status = gr.Textbox(label="Status", interactive=False)
            
            def process_with_status(audio, src_lang, tgt_lang, progress=gr.Progress()):
                try:
                    if audio is None or (isinstance(audio, dict) and not audio.get('path')):
                        raise gr.Error("Please provide an audio input!")
                    
                    # Extract the actual audio path or data
                    if isinstance(audio, dict):
                        audio_input = audio.get('name') or audio.get('path')
                    else:
                        audio_input = audio
                    
                    if not audio_input:
                        raise gr.Error("Invalid audio input")
                    
                    # Process with progress updates
                    progress(0.33, desc="Transcribing")
                    source_text, translated_text, output_path = self.process_audio(audio_input, src_lang, tgt_lang)
                    progress(1.0, desc="Complete")
                    
                    return source_text, translated_text, output_path, "Success! ✨"
                except Exception as e:
                    error_msg = str(e)
                    return None, None, None, f"Error: {error_msg}"

            submit_btn.click(
                fn=process_with_status,
                inputs=[audio_input, source_lang, target_lang],
                outputs=[transcription, translation, output_audio, status]
            )
            
            gr.Markdown("""
            ### How to use:
            1. Select source and target languages
            2. Record audio or upload an audio file
            3. Click 'Translate' and wait for the magic!
            """)
        
        return interface

if __name__ == "__main__":
    # For testing locally
    app = VoxLingo()
    interface = app.create_interface()
    interface.launch(share=True)
