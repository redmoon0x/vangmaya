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

## Usage

1. Place your audio file in the project directory or specify its path.

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
