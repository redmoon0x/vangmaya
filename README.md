---
title: VoxLingo
emoji: 🎙️
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.25.2
app_file: app.py
pinned: false
---

# 🎙️ VoxLingo - Indian Language Voice Translator

VoxLingo is a powerful voice translation application that lets you speak in one Indian language and get the translation in another while preserving your original voice! It combines three AI technologies:

1. Voice-to-Text (AI4Bharat ASR)
2. Text Translation (Anuvaad)
3. Voice Cloning & Speech Synthesis (AI4Bharat IndicF5)

## Features

- 🗣️ Support for 22 Indian languages
- 🎤 Record audio or upload audio files
- 🔄 Real-time voice translation
- 🎯 Voice preservation in translated audio
- 🎵 High-quality speech synthesis

## Supported Languages

- Hindi (hi)
- Kannada (kn)
- Tamil (ta)
- Telugu (te)
- Malayalam (ml)
- Bengali (bn)
- Marathi (mr)
- Gujarati (gu)
- And many more!

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python voxlingo.py
```

## Deploying to Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Choose 'Gradio' as the SDK
3. Upload these files to your Space:
   - voxlingo.py
   - voice_to_text.py
   - translator.py
   - text_to_speech.py
   - requirements.txt
   - README.md

The app will automatically deploy and be available at your Space's URL.

## How It Works

1. **Voice-to-Text**: Uses AI4Bharat's ASR service to convert speech to text
2. **Translation**: Uses Anuvaad for accurate translation between Indian languages
3. **Text-to-Speech**: Uses AI4Bharat's IndicF5 model to synthesize speech while preserving the original voice characteristics

## Note

This application requires an internet connection as it uses various AI models hosted online.
