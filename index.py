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
    # Serves the interface seamlessly from memory to prevent file routing bugs
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text-to-Speech & Translator</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #f4f7f6;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 500px;
        }
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 15px;
            margin-bottom: 5px;
            color: #555;
        }
        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            resize: none;
            font-size: 14px;
        }
        .checkbox-container {
            display: flex;
            align-items: center;
            margin: 15px 0;
        }
        .checkbox-container input {
            margin-right: 10px;
        }
        select {
            width: 100%;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
            background: white;
            font-size: 14px;
        }
        .status {
            font-style: italic;
            color: gray;
            margin: 15px 0;
            min-height: 20px;
            font-size: 14px;
        }
        .btn-group {
            display: flex;
            gap: 10px;
        }
        button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-speak { background-color: #0070f3; color: white; }
        .btn-speak:hover { background-color: #0051cb; }
        .btn-download { background-color: #10b981; color: white; }
        .btn-download:hover { background-color: #059669; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }
        audio { width: 100%; margin-top: 20px; display: none; }
    </style>
</head>
<body>

<div class="container">
    <h2>Web TTS & Translator</h2>
    
    <label>Type your text here (Any language):</label>
    <textarea id="textInput" placeholder="Enter text to convert..."></textarea>
    
    <div class="checkbox-container">
        <input type="checkbox" id="translateCheck" checked>
        <label style="margin:0; font-weight:normal;" for="translateCheck">Translate text before speaking</label>
    </div>
    
    <label>Target Accent:</label>
    <select id="accentSelect">
        <option value="English (United States)">English (United States)</option>
        <option value="English (United Kingdom)">English (United Kingdom)</option>
        <option value="English (India)">English (India)</option>
        <option value="English (Australia)">English (Australia)</option>
        <option value="Spanish (Spain)">Spanish (Spain)</option>
        <option value="Spanish (Mexico)">Spanish (Mexico)</option>
        <option value="French (France)">French (France)</option>
        <option value="German (Germany)">German (Germany)</option>
        <option value="Hindi (India)">Hindi (India)</option>
        <option value="Chinese (Mandarin)">Chinese (Mandarin)</option>
    </select>
    
    <label>Voice Gender:</label>
    <select id="genderSelect">
        <option value="Female">Female</option>
        <option value="Male">Male</option>
    </select>
    
    <div class="status" id="statusLabel">Ready</div>
    
    <div class="btn-group">
        <button class="btn-speak" id="speakBtn" onclick="processAudio('play')">Speak</button>
        <button class="btn-download" id="downloadBtn" onclick="processAudio('download')">Download MP3</button>
    </div>
    
    <audio id="audioPlayer" controls></audio>
</div>

<script>
    async function processAudio(actionType) {
        const text = document.getElementById('textInput').value.trim();
        const translate = document.getElementById('translateCheck').checked;
        const accent = document.getElementById('accentSelect').value;
        const gender = document.getElementById('genderSelect').value;
        
        const statusLabel = document.getElementById('statusLabel');
        const speakBtn = document.getElementById('speakBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const player = document.getElementById('audioPlayer');

        if (!text) {
            alert("Please enter some text first!");
            return;
        }

        speakBtn.disabled = true;
        downloadBtn.disabled = true;
        statusLabel.textContent = "Processing and generating audio... Please wait.";
        statusLabel.style.color = "#0070f3";

        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, translate, accent, gender })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Server error occurred");
            }

            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);

            statusLabel.textContent = "Audio generated successfully!";
            statusLabel.style.color = "#10b981";

            if (actionType === 'play') {
                player.src = audioUrl;
                player.style.display = "block";
                player.play();
            } else if (actionType === 'download') {
                const a = document.createElement('a');
                a.href = audioUrl;
                a.download = "speech.mp3";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }

        } catch (error) {
            statusLabel.textContent = "Error: " + error.message;
            statusLabel.style.color = "#ef4444";
        } finally {
            speakBtn.disabled = false;
            downloadBtn.disabled = false;
        }
    }
</script>

</body>
</html>'''