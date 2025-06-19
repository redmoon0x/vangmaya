# Voice and Text Translation System

A robust system for voice-to-text conversion and text translation with built-in proxy rotation and header management.

## Features

### Core Functionality
- Voice to Text conversion
- Text translation between multiple Indian languages
- Support for 22+ languages

### Request Management
- Automatic proxy rotation
- Dynamic header generation
- User agent rotation
- Multiple origin support

## Project Structure

```
├── src/
│   ├── proxy_manager.py      # Proxy fetching and testing
│   ├── request_manager.py    # Request handling with rotation
│   ├── headers_manager.py    # Dynamic header generation
│   └── user_agent_rotator.py # User agent rotation
├── voice_to_text.py         # Voice to text conversion
├── translator.py            # Text translation
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Usage example:

```python
# Voice to Text
from voice_to_text import VoiceToTextConverter

converter = VoiceToTextConverter()
result = converter.transcribe("audio_file.mp3", "hi")  # Hindi transcription

# Translation
from translator import TextTranslator

translator = TextTranslator()
result = translator.translate(
    text="Hello, how are you?",
    target_lang="hi",  # Hindi
    source_lang="en"   # English
)
```

## Supported Languages

Both voice-to-text and translation support a wide range of Indian languages:

- Hindi (hi)
- Bengali (bn)
- Gujarati (gu)
- Kannada (kn)
- Malayalam (ml)
- Marathi (mr)
- Punjabi (pa)
- Tamil (ta)
- Telugu (te)
- And many more...

## Features

### Request Management
- Automatic proxy rotation with speed testing
- Proxy failover and retry logic
- HTTP/HTTPS support with SSL handling

### Header Management
- Dynamic header generation
- Multiple origin domains
- Randomized accept-language headers
- Secure header configuration

### Performance
- Proxy speed testing and ranking
- Fast proxy reuse
- Connection pooling
- Automatic retry on failure
