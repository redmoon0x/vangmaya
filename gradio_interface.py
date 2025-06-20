import gradio as gr
import logging
import os
from audio_translation_pipeline import AudioTranslationPipeline

# Configure logging - suppress all but critical errors
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Suppress all loggers except critical errors
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.ERROR)

# Initialize pipeline
pipeline = AudioTranslationPipeline()

# Define available languages
LANGUAGES = {
    "Kannada": "kn",
    "Hindi": "hi",
    "English": "en",
    "Telugu": "te",
    "Tamil": "ta",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Punjabi": "pa"
}

def process_audio(audio_path, source_lang, target_lang, api_url):
    # Update the API URL
    os.environ['TTS_API_URL'] = api_url
    try:
        if audio_path is None:
            return "Please provide an audio input.", None
            
        # Display processing message
        gr.Info("Processing audio. Please wait...")
            
        # Process the audio file
        result = pipeline.process(
            audio_file_path=audio_path,
            source_lang=LANGUAGES[source_lang],
            target_lang=LANGUAGES[target_lang]
        )
        
        output_text = f"""
Original Text ({source_lang}): {result['original_text']}

Translated Text ({target_lang}): {result['translated_text']}
"""
        return output_text, result['audio_path']
        
    except Exception as e:
        error_msg = str(e)
        if "All proxies failed" in error_msg:
            return "Sorry, the service is temporarily unavailable. Please try again in a few moments.", None
        return f"Error: {error_msg}", None

# Create Gradio interface
def create_interface():
    interface = gr.Interface(
        fn=process_audio,
        inputs=[
            gr.Audio(type="filepath", label="Upload audio or Record"),
            gr.Dropdown(choices=list(LANGUAGES.keys()), label="Source Language"),
            gr.Dropdown(choices=list(LANGUAGES.keys()), label="Target Language"),
            gr.Textbox(
                label="TTS API URL", 
                value="https://geometry-remembered-war-mj.trycloudflare.com/",
                placeholder="Enter the TTS API URL"
            )
        ],
        outputs=[
            gr.Textbox(label="Translation Results"),
            gr.Audio(label="Translated Audio")
        ],
        title="Audio Translation Pipeline",
        description="Upload or record audio, select source and target languages to translate audio content."
    )
    return interface

if __name__ == "__main__":
    demo = create_interface()
    # Launch without attempting to create a share link
    demo.launch(share=True)
