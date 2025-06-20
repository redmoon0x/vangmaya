# Audio Translation Pipeline

A Python pipeline that converts audio to text and then translates it to the desired language. This pipeline combines voice recognition and translation capabilities to process audio files in multiple Indian languages.

## Features

- Voice to text conversion for multiple Indian languages
- Text translation between supported languages
- Robust error handling and logging
- Simple and intuitive API

## Prerequisites

- Python 3.8 or higher
- `pip` package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── src/
│   ├── headers_manager.py
│   ├── proxy_manager.py
│   ├── request_manager.py
│   └── user_agent_rotator.py
├── uploads/               # Directory for audio files
├── audio_translation_pipeline.py
├── voice_to_text.py
├── translator.py
├── example_usage.py
└── requirements.txt
```

## Web Interface

The project includes a Gradio web interface that makes it easy to use the translation pipeline. You can:
- Upload or record audio directly in the browser
- Select source and target languages from dropdown menus
- Configure the TTS API URL
- Get instant results with translated text and audio

### Running the Web Interface Locally

```bash
python app.py
```

The interface will be available at http://localhost:7860

### Deploying to Hugging Face Spaces

1. Create a new Space on Hugging Face:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose "Gradio" as the SDK
   - Set Python version to 3.8 or higher

2. Upload the following files to your Space:
   - `app.py`
   - `gradio_interface.py`
   - `audio_translation_pipeline.py`
   - `voice_to_text.py`
   - `translator.py`
   - `text_to_speech.py`
   - `requirements.txt`
   - All files in the `src/` directory

3. Configure your Space:
   - Go to your Space's Settings > Repository Secrets
   - Add the following secrets (optional):
     - `TTS_API_URL`: Your default TTS API URL (if you want to override the default)
     
4. The Space will automatically deploy your application.

5. Configure the TTS API URL:
   - When using the interface, you can input your TTS API URL
   - The default URL is configurable in two ways:
     a. Through the interface directly
     b. By setting the `TTS_API_URL` environment variable/secret

## Configuration

### Environment Variables

The following environment variables can be configured:

- `TTS_API_URL`: The URL for the Text-to-Speech API service
  - Default: "https://geometry-remembered-war-mj.trycloudflare.com/"
  - Can be overridden through:
    - Environment variable
    - Hugging Face Space secret
    - Web interface input

### Local Configuration

When running locally, you can set environment variables in several ways:

1. In your shell:
```bash
export TTS_API_URL="your-api-url"
python app.py
```

2. Using a .env file:
```env
TTS_API_URL=your-api-url
```

3. Or directly through the web interface

### Hugging Face Space Configuration

In your Hugging Face Space:

1. Go to Settings > Repository Secrets
2. Add your secrets:
   - Click "New Secret"
   - Name: TTS_API_URL
   - Value: Your API URL

This configuration will be automatically loaded when your Space starts.

## Usage

1. Using the Web Interface (Recommended):
   - Open the application in your browser
   - Upload or record an audio file
   - Select source and target languages
   - Enter your TTS API URL
   - Click submit to process the audio

2. Using the Python API:

2. Use the pipeline in your Python code:

```python
from audio_translation_pipeline import AudioTranslationPipeline

# Initialize the pipeline
pipeline = AudioTranslationPipeline()

# Process an audio file
result = pipeline.process(
    audio_file_path="path/to/your/audio.mp3",
    source_lang="hi",  # Source language code
    target_lang="en"   # Target language code
)

# Print results
print(f"Original Text: {result['original_text']}")
print(f"Translated Text: {result['translated_text']}")
```

3. Or run the example script:
```bash
python example_usage.py
```

## Supported Languages

The pipeline supports the following languages (codes in brackets):

- Hindi (hi)
- English (en)
- Marathi (mr)
- Bengali (bn)
- Gujarati (gu)
- Kannada (kn)
- Malayalam (ml)
- Odia (or)
- Punjabi (pa)
- Tamil (ta)
- Telugu (te)
- And more...

Use `get_supported_languages()` to see the complete list of supported languages:

```python
pipeline = AudioTranslationPipeline()
languages = pipeline.get_supported_languages()
for code, name in languages.items():
    print(f"{code}: {name}")
```

## Error Handling

The pipeline includes comprehensive error handling for:
- Invalid language codes
- Missing audio files
- Network connectivity issues
- API service availability
- Invalid audio formats

Errors are logged with detailed messages to help diagnose issues.

## Testing

Run the test suite:
```bash
python -m unittest test_audio_translation_pipeline.py
```

## Troubleshooting

If you encounter issues:

1. Check that your audio file exists and is in a supported format
2. Verify that the source and target languages are supported
3. Ensure you have an active internet connection
4. Check the logs for detailed error messages
5. Make sure all dependencies are installed correctly

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
