import gradio as gr
import logging
import os
from audio_translation_pipeline import AudioTranslationPipeline

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.ERROR)

pipeline = AudioTranslationPipeline()

LANGUAGES = {
    "Hindi (हिन्दी)": "hi",
    "English": "en",
    "Bengali (বাংলা)": "bn",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Marathi (मराठी)": "mr",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Gujarati (ગુજરાતી)": "gu",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa"
}

def process_audio(audio_path, source_lang, target_lang):
    try:
        if audio_path is None:
            return "Please upload or record audio to translate.", None
            
        gr.Info("Processing your audio...")
        result = pipeline.process(
            audio_file_path=audio_path,
            source_lang=LANGUAGES[source_lang],
            target_lang=LANGUAGES[target_lang]
        )
        
        output_text = f"Original ({source_lang}):\n{result['original_text']}\n\nTranslation ({target_lang}):\n{result['translated_text']}"
        return output_text, result['audio_path']
        
    except Exception as e:
        error_msg = str(e)
        if "All proxies failed" in error_msg:
            return "Service is busy. Please try again in a moment.", None
        return f"Error: {error_msg}", None

def create_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# ವಾಙ್ಮಯ (Vangmaya)")
        gr.Markdown("""
        ### Breaking Language Barriers, Keeping Your Identity
        
        Experience the future of voice translation. ವಾಙ್ಮಯ uniquely preserves your voice while translating 
        your speech into any Indian language. Built on AI4Bharat's groundbreaking voice cloning technology, 
        it ensures your message reaches millions while staying authentically you.
        """)
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    type="filepath",
                    label="Upload or Record Audio"
                )
                with gr.Row():
                    source_lang = gr.Dropdown(
                        choices=list(LANGUAGES.keys()),
                        value="English",
                        label="From"
                    )
                    target_lang = gr.Dropdown(
                        choices=list(LANGUAGES.keys()),
                        value="Hindi (हिन्दी)",
                        label="To"
                    )
                process_btn = gr.Button("Translate")

            with gr.Column():
                text_output = gr.Textbox(
                    label="Translation Results",
                    lines=4
                )
                audio_output = gr.Audio(
                    label="Translated Audio"
                )
                
        gr.Markdown("""
        ---
        #### How is it revolutionary?
        - First system to maintain speaker identity across Indian languages
        - Zero-shot voice cloning - works instantly with any voice
        - State-of-the-art neural speech synthesis from IIT Madras
        - Preserves emotion and speaking style during translation
        """)

        process_btn.click(
            fn=process_audio,
            inputs=[audio_input, source_lang, target_lang],
            outputs=[text_output, audio_output]
        )
        
        gr.Markdown("""
        ---
        *Breaking the language barrier across 1.4 billion Indian voices, one conversation at a time.  
        A project by AI4Bharat, fostering communication in a linguistically diverse India.*
        """)

    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.queue().launch(
        share=True,
        debug=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
