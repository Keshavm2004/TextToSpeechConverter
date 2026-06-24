import os
import asyncio
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator
import edge_tts
import urllib.parse

app = Flask(__name__)
CORS(app)

# Exhaustive baseline localization map array dictionary footprint layout translation strings
LOCALE_MAP = {
    "af-ZA": "Afrikaans (South Africa)", "am-ET": "Amharic (Ethiopia)", 
    "ar-AE": "Arabic (UAE)", "ar-BH": "Arabic (Bahrain)", "ar-DZ": "Arabic (Algeria)", 
    "ar-EG": "Arabic (Egypt)", "ar-IQ": "Arabic (Iraq)", "ar-JO": "Arabic (Jordan)", 
    "ar-KW": "Arabic (Kuwait)", "ar-LB": "Arabic (Lebanon)", "ar-LY": "Arabic (Libya)", 
    "ar-MA": "Arabic (Morocco)", "ar-OM": "Arabic (Oman)", "ar-PS": "Arabic (Palestine)", 
    "ar-QA": "Arabic (Qatar)", "ar-SA": "Arabic (Saudi Arabia)", "ar-SY": "Arabic (Syria)", 
    "ar-TN": "Arabic (Tunisia)", "ar-YE": "Arabic (Yemen)", "az-AZ": "Azerbaijani (Azerbaijan)", 
    "bg-BG": "Bulgarian (Bulgaria)", "bn-BD": "Bengali (Bangladesh)", "bn-IN": "Bengali (India)", 
    "bs-BA": "Bosnian (Bosnia)", "ca-ES": "Catalan (Spain)", "cs-CZ": "Czech (Czechia)", 
    "cy-GB": "Welsh (United Kingdom)", "da-DK": "Danish (Denmark)", "de-AT": "German (Austria)", 
    "de-CH": "German (Switzerland)", "de-DE": "German (Germany)", "el-GR": "Greek (Greece)", 
    "en-AU": "English (Australia)", "en-CA": "English (Canada)", "en-GB": "English (United Kingdom)", 
    "en-HK": "English (Hong Kong)", "en-IE": "English (Ireland)", "en-IN": "English (India)", 
    "en-KE": "English (Kenya)", "en-NG": "English (Nigeria)", "en-NZ": "English (New Zealand)", 
    "en-PH": "English (Philippines)", "en-SG": "English (Singapore)", "en-TZ": "English (Tanzania)", 
    "en-US": "English (United States)", "en-ZA": "English (South Africa)", "es-AR": "Spanish (Argentina)", 
    "es-BO": "Spanish (Bolivia)", "es-CL": "Spanish (Chile)", "es-CO": "Spanish (Colombia)", 
    "es-CR": "Spanish (Costa Rica)", "es-CU": "Spanish (Cuba)", "es-DO": "Spanish (Dominican Republic)", 
    "es-EC": "Spanish (Ecuador)", "es-ES": "Spanish (Spain)", "es-GQ": "Spanish (Equatorial Guinea)", 
    "es-GT": "Spanish (Guatemala)", "es-HN": "Spanish (Honduras)", "es-MX": "Spanish (Mexico)", 
    "es-NI": "Spanish (Nicaragua)", "es-PA": "Spanish (Panama)", "es-PE": "Spanish (Peru)", 
    "es-PR": "Spanish (Puerto Rico)", "es-PY": "Spanish (Paraguay)", "es-SV": "Spanish (El Salvador)", 
    "es-US": "Spanish (United States)", "es-UY": "Spanish (Uruguay)", "es-VE": "Spanish (Venezuela)", 
    "et-EE": "Estonian (Estonia)", "eu-ES": "Basque (Spain)", "fa-IR": "Persian (Iran)", 
    "fi-FI": "Finnish (Finland)", "fil-PH": "Filipino (Philippines)", "fr-BE": "French (Belgium)", 
    "fr-CA": "French (Canada)", "fr-CH": "French (Switzerland)", "fr-FR": "French (France)", 
    "ga-IE": "Irish (Ireland)", "gl-ES": "Galician (Spain)", "gu-IN": "Gujarati (India)", 
    "he-IL": "Hebrew (Israel)", "hi-IN": "Hindi (India)", "hr-HR": "Croatian (Croatia)", 
    "hu-HU": "Hungarian (Hungary)", "hy-AM": "Armenian (Armenia)", "id-ID": "Indonesian (Indonesia)", 
    "is-IS": "Icelandic (Iceland)", "it-IT": "Italian (Italy)", "ja-JP": "Japanese (Japan)", 
    "jv-ID": "Javanese (Indonesia)", "ka-GE": "Georgian (Georgia)", "kk-KZ": "Kazakh (Kazakhstan)", 
    "km-KH": "Khmer (Cambodia)", "kn-IN": "Kannada (India)", "ko-KR": "Korean (Korea)", 
    "lo-LA": "Lao (Laos)", "lt-LT": "Lithuanian (Lithuania)", "lv-LV": "Latvian (Latvia)", 
    "mk-MK": "Macedonian (North Macedonia)", "ml-IN": "Malayalam (India)", "mn-MN": "Mongolian (Mongolia)", 
    "mr-IN": "Marathi (India)", "ms-MY": "Malay (Malaysia)", "mt-MT": "Maltese (Malta)", 
    "my-MM": "Burmese (Myanmar)", "nb-NO": "Norwegian Bokmål (Norway)", "ne-NP": "Nepali (Nepal)", 
    "nl-BE": "Dutch (Belgium)", "nl-NL": "Dutch (Netherlands)", "pa-IN": "Punjabi (India)", 
    "pl-PL": "Polish (Poland)", "ps-AF": "Pashto (Afghanistan)", "pt-BR": "Portuguese (Brazil)", 
    "pt-PT": "Portuguese (Portugal)", "ro-RO": "Romanian (Romania)", "ru-RU": "Russian (Russia)", 
    "si-LK": "Sinhala (Sri Lanka)", "sk-SK": "Slovak (Slovakia)", "sl-SI": "Slovenian (Slovenia)", 
    "so-SO": "Somali (Somalia)", "sq-AL": "Albanian (Albania)", "sr-RS": "Serbian (Serbia)", 
    "su-ID": "Sundanese (Indonesia)", "sv-SE": "Swedish (Sweden)", "sw-KE": "Swahili (Kenya)", 
    "sw-TZ": "Swahili (Tanzania)", "ta-IN": "Tamil (India)", "ta-LK": "Tamil (Sri Lanka)", 
    "ta-MY": "Tamil (Malaysia)", "ta-SG": "Tamil (Singapore)", "te-IN": "Telugu (India)", 
    "th-TH": "Thai (Thailand)", "tr-TR": "Turkish (Turkey)", "uk-UA": "Ukrainian (Ukraine)", 
    "ur-IN": "Urdu (India)", "ur-PK": "Urdu (Pakistan)", "uz-UZ": "Uzbek (Uzbekistan)", 
    "vi-VN": "Vietnamese (Vietnam)", "zh-CN": "Chinese (Mainland)", "zh-HK": "Chinese (Hong Kong)", 
    "zh-TW": "Chinese (Taiwan)", "zu-ZA": "Zulu (South Africa)"
}

def load_all_voices():
    """Dynamically parses and structuralizes complete server voice lists across Edge TTS."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        voices = loop.run_until_complete(edge_tts.list_voices())
        loop.close()
    except Exception:
        # Static absolute structural fallback contingency layout loop rules
        return {
            "English (United States)": {"lang": "en", "Female": ["en-US-AvaNeural"], "Male": ["en-US-GuyNeural"]},
            "Hindi (India)": {"lang": "hi", "Female": ["hi-IN-SwaraNeural"], "Male": ["hi-IN-MadhurNeural"]}
        }
    
    options = {}
    for voice in voices:
        locale_code = voice.get("Locale", "")
        gender = voice.get("Gender", "Female")
        short_name = voice.get("ShortName", "")
        
        lang_code = locale_code.split('-')[0]
        label_name = LOCALE_MAP.get(locale_code, f"{locale_code} (Regional Accent)")
        
        if label_name not in options:
            options[label_name] = {
                "lang": lang_code,
                "Female": [],
                "Male": []
            }
        
        if gender in ["Female", "Male"]:
            options[label_name][gender].append(short_name)
            
    return {k: options[k] for k in sorted(options.keys())}

# Live tracking initial configuration setup global mapping injection instance
VOICE_OPTIONS = load_all_voices()

async def generate_voice_file(text, voice_name, output_path, rate_string):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate_string)
    await communicate.save(output_path)

@app.route('/api/voices', methods=['GET'])
def get_voices_manifest():
    """Provides UI with full layout metadata context options directly."""
    return jsonify(VOICE_OPTIONS)

@app.route('/api/tts', methods=['POST'])
def tts_api():
    data = request.get_json() or {}
    
    text = data.get('text', '').strip()
    accent = data.get('accent', 'English (United States)')
    gender = data.get('gender', 'Female')
    translate = data.get('translate', True)
    variant_idx = data.get('variant_index', 0)
    speed = data.get('speed', 1.0)
    
    if not text:
        return jsonify(error="Text payload is required"), 400
        
    if accent not in VOICE_OPTIONS:
        return jsonify(error="Invalid accent profile option tracking selected"), 400

    voice_config = VOICE_OPTIONS[accent]
    target_lang = voice_config["lang"]

    # Fallback safety guardrails matching desktop configuration mapping variants loops
    available_voices = voice_config.get(gender, [])
    if not available_voices:
        fallback_gender = "Male" if gender == "Female" else "Female"
        available_voices = voice_config.get(fallback_gender, [])
        if available_voices:
            gender = fallback_gender
        else:
            return jsonify(error="No usable actors detected inside requested region profile data parameters."), 400

    try:
        voice_name = available_voices[variant_idx]
    except (IndexError, TypeError):
        voice_name = available_voices[0]

    # Calculate Edge-TTS structural string offset parsing constraints
    percentage_offset = int((float(speed) - 1.0) * 100)
    rate_string = f"+{percentage_offset}%" if percentage_offset >= 0 else f"{percentage_offset}%"

    # 1. Translation Processing
    if translate:
        try:
            processed_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            return jsonify(error=f"Translation engine error: {str(e)}"), 500
    else:
        processed_text = text

    # 2. Audio Generation
    temp_output_path = "/tmp/output_speech.mp3"
    try:
        asyncio.run(generate_voice_file(processed_text, voice_name, temp_output_path, rate_string))
    except Exception as e:
        return jsonify(error=f"Audio generation error: {str(e)}"), 500

    # 3. Stream audio file back to client WITH the translated text header
    response = send_file(temp_output_path, mimetype="audio/mp3")
    
    # URL-encode text to handle non-ASCII characters cleanly in HTTP headers
    response.headers["X-Translated-Text"] = urllib.parse.quote(processed_text)
    # Expose the header so browser JavaScript can read it
    response.headers["Access-Control-Expose-Headers"] = "X-Translated-Text"
    
    return response

@app.route('/')
def home():
    # Looks for index.html in the same directory and serves it to the browser
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_file(os.path.join(base_dir, 'index.html'))
