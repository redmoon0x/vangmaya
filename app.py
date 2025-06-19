from flask import Flask, render_template, request, jsonify, send_file
import os
from voice_to_text import VoiceToTextConverter
from translator import TextTranslator
import tempfile
import numpy as np
import soundfile as sf
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
                    audio_array = np.array(speech_data)
                    audio_array = audio_array / np.max(np.abs(audio_array))
                    sf.write(audio_path, audio_array, 16000, subtype='PCM_16')
                    
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

pipeline = VoiceTranslationPipeline()

def get_supported_languages():
    converter = VoiceToTextConverter()
    translator = TextTranslator()
    
    all_langs = converter.get_supported_languages()
    target_langs = {
        code: name for code, name in all_langs.items()
        if name in [
            "Assamese", "Bengali", "Gujarati", "Hindi", 
            "Kannada", "Malayalam", "Marathi", "Odia",
            "Punjabi", "Tamil", "Telugu"
        ]
    }
    return all_langs, target_langs

@app.route('/')
def index():
    all_langs, target_langs = get_supported_languages()
    return render_template('index.html', 
                         source_languages=all_langs,
                         target_languages=target_langs)

@app.route('/translate', methods=['POST'])
def translate():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    source_lang = request.form.get('source_lang', 'en')
    target_lang = request.form.get('target_lang', 'hi')
    
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Save the uploaded file
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.wav')
    audio_file.save(audio_path)
    
    try:
        result = pipeline.process(audio_path, source_lang, target_lang)
        return jsonify({
            'transcribed_text': result['transcribed_text'],
            'translated_text': result['translated_text'],
            'audio_path': result['output_audio']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup the temporary uploaded file
        if os.path.exists(audio_path):
            os.remove(audio_path)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    try:
        return send_file(filename, mimetype='audio/wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
