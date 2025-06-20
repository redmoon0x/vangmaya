---
title: Audio Translation Interface
emoji: 🗣️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 3.50.2
app_file: app.py
pinned: false
---

# Audio Translation Web Interface

This is a web interface for translating audio between different Indian languages. You can upload or record audio in one language and get both text and audio output in another language.

## Features

- Voice to text conversion
- Text translation between languages
- Text to speech synthesis
- Support for multiple Indian languages
- User-configurable TTS API URL

## Supported Languages

- Hindi (hi)
- English (en)
- Telugu (te)
- Tamil (ta)
- Kannada (kn)
- Malayalam (ml)
- Bengali (bn)
- Gujarati (gu)
- Marathi (mr)
- Punjabi (pa)

## How to Use

1. Upload an audio file or record directly through the interface
2. Select the source language (language of the audio)
3. Select the target language (language to translate to)
4. Configure the TTS API URL if needed
5. Click submit to process the audio

The interface will return:
- Original text in source language
- Translated text in target language
- Audio file of the translated text

## API Configuration

The TTS API URL can be configured directly through the interface. The default URL is:
```
https://geometry-remembered-war-mj.trycloudflare.com/
```

If you have your own TTS API endpoint, you can enter it in the text box provided.

## Troubleshooting

If you encounter issues:
1. Check that your audio file is in a supported format (WAV, MP3, FLAC)
2. Verify that the source and target languages are correctly selected
3. Ensure you have a working internet connection
4. For TTS issues, verify the API URL is correct and accessible
