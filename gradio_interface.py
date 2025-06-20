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

# Define available languages with native names
LANGUAGES = {
    "Kannada (ಕನ್ನಡ)": "kn",
    "Hindi (हिन्दी)": "hi",
    "English": "en",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Marathi (मराठी)": "mr",
    "Bengali (বাংলা)": "bn",
    "Gujarati (ગુજરાતી)": "gu",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa"
}

def process_audio(audio_path, source_lang, target_lang):
    try:
        if audio_path is None:
            return "Please provide an audio input.", None
            
        # Display processing message
        gr.Info("Processing audio...")
            
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
            return "Service temporarily unavailable. Please try again in a few moments.", None
        return f"Error: {error_msg}", None

def create_interface():
    # CSS for custom styling
    css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    h1 {
        color: #B22025 !important;  /* Traditional Indian Red */
        text-align: center !important;
        font-size: 2.5em !important;
        margin-bottom: 0.2em !important;
    }
    .subtitle {
        color: #666 !important;
        text-align: center !important;
        font-size: 1.2em !important;
        margin-bottom: 2em !important;
    }
    .features {
        background: #FFF9E6;  /* Light warm background */
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .disclaimer {
        text-align: center;
        font-size: 0.9em;
        color: #666;
        border-top: 1px solid #ddd;
        padding-top: 20px;
        margin-top: 40px;
    }
    button.primary {
        background: #B22025 !important;
        border: none !important;
    }
    button.primary:hover {
        background: #8B1821 !important;
    }
    """
    
    theme = gr.themes.Soft(
        primary_hue="red",
        secondary_hue="orange",
        font=["Arial", "sans-serif"]
    )
    
    with gr.Blocks(css=css, theme=theme) as interface:
        gr.Markdown("# ವಾಙ್ಮಯ (Vangmaya)")
        gr.Markdown("#### Your Voice, Any Indian Language", elem_classes="subtitle")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    type="filepath",
                    label="🎙️ Upload or Record Audio",
                    elem_classes="audio-input"
                )
                source_lang = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="English",  # Default source language
                    label="Source Language"
                )
                target_lang = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="Hindi (हिन्दी)",  # Default target language
                    label="Target Language"
                )
                process_btn = gr.Button("🔄 Translate", variant="primary")

            with gr.Column():
                text_output = gr.Textbox(label="Translation Results")
                audio_output = gr.Audio(label="Translated Audio")
        
        # Description and features
        gr.Markdown("""
        ### ✨ Features
        - 🗣️ Translate speech while preserving your voice
        - 🔤 Support for 10 major Indian languages
        - 🎯 AI-powered voice cloning
        - ⚡ Fast and efficient processing
        
        Simply speak in your language, and Vangmaya will transform it while keeping your voice intact!
        """)
        
        # Add processing function
        process_btn.click(
            fn=process_audio,
            inputs=[audio_input, source_lang, target_lang],
            outputs=[text_output, audio_output]
        )
        
        gr.Markdown("""
        ---
        Powered by state-of-the-art AI technology from AI4Bharat (IIT Madras).  
        Note: ವಾಙ್ಮಯ (Vangmaya) means "speech" or "verbal expression" in Sanskrit.
        """, elem_classes="disclaimer")
    return interface

if __name__ == "__main__":
    interface = create_interface()
    # Launch with queue enabled
    interface.queue().launch(
        share=True,
        debug=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
