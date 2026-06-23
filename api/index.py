import os
import asyncio
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator
import edge_tts

app = Flask(__name__)
CORS(app)  # Allows web browsers to safely connect to your API

# Mirrored directly from your desktop app configuration
VOICE_OPTIONS = {
    "English (United States)": {"Male": "en-US-GuyNeural", "Female": "en-US-AvaNeural", "lang": "en"},
    "English (United Kingdom)": {"Male": "en-GB-RyanNeural", "Female": "en-GB-SoniaNeural", "lang": "en"},
    "English (India)": {"Male": "en-IN-PrabhatNeural", "Female": "en-IN-NeerjaNeural", "lang": "en"},
    "English (Australia)": {"Male": "en-AU-WilliamNeural", "Female": "en-AU-NatashaNeural", "lang": "en"},
    "Spanish (Spain)": {"Male": "es-ES-AlvaroNeural", "Female": "es-ES-ElviraNeural", "lang": "es"},
    "Spanish (Mexico)": {"Male": "es-MX-JorgeNeural", "Female": "es-MX-DaliaNeural", "lang": "es"},
    "French (France)": {"Male": "fr-FR-HenriNeural", "Female": "fr-FR-DeniseNeural", "lang": "fr"},
    "French (Canada)": {"Male": "fr-CA-LiamNeural", "Female": "fr-CA-SylvieNeural", "lang": "fr"},
    "German (Germany)": {"Male": "de-DE-ConradNeural", "Female": "de-DE-AmalaNeural", "lang": "de"},
    "Hindi (India)": {"Male": "hi-IN-MadhurNeural", "Female": "hi-IN-SwaraNeural", "lang": "hi"},
    "Chinese (Mandarin)": {"Male": "zh-CN-YunxiNeural", "Female": "zh-CN-XiaoxiaoNeural", "lang": "zh-CN"}
}

async def generate_voice_file(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

@app.route('/api/tts', methods=['POST'])
def tts_api():
    data = request.get_json() or {}
    
    text = data.get('text', '').strip()
    accent = data.get('accent', 'English (United States)')
    gender = data.get('gender', 'Female')
    translate = data.get('translate', True)
    
    if not text:
        return jsonify(error="Text payload is required"), 400
        
    if accent not in VOICE_OPTIONS:
        return jsonify(error="Invalid accent selected"), 400

    voice_config = VOICE_OPTIONS[accent]
    target_lang = voice_config["lang"]
    voice_name = voice_config[gender]

    # 1. Translation Processing
    if translate:
        try:
            processed_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            return jsonify(error=f"Translation engine error: {str(e)}"), 500
    else:
        processed_text = text

    # 2. Audio Generation (Vercel environments only allow writing to /tmp)
    temp_output_path = "/tmp/output_speech.mp3"
    try:
        asyncio.run(generate_voice_file(processed_text, voice_name, temp_output_path))
    except Exception as e:
        return jsonify(error=f"Audio generation error: {str(e)}"), 500

    # 3. Stream audio file back to client
    return send_file(temp_output_path, mimetype="audio/mp3")

@app.route('/')
def home():
    # Automatically read and serve the index.html file located in the root directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'index.html')
    return send_file(html_path)