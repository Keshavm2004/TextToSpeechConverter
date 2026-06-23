# voices.py
import asyncio
import edge_tts

# A comprehensive mapping to give polished, friendly names to Microsoft Edge locale codes
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
    """
    Synchronously extracts the live async voice manifest from Microsoft Edge TTS 
    to sort every model by geographic region and gender structure.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        voices = loop.run_until_complete(edge_tts.list_voices())
        loop.close()
    except Exception:
        # Secure local fallback if application starts up completely offline
        return {
            "English (United States)": {"lang": "en", "Female": ["en-US-AvaNeural"], "Male": ["en-US-GuyNeural"]},
            "Hindi (India)": {"lang": "hi", "Female": ["hi-IN-SwaraNeural"], "Male": ["hi-IN-MadhurNeural"]}
        }
    
    options = {}
    for voice in voices:
        locale_code = voice.get("Locale", "")
        gender = voice.get("Gender", "Female")
        short_name = voice.get("ShortName", "")
        
        # Isolate base translator engine tag (e.g., 'en' from 'en-US')
        lang_code = locale_code.split('-')[0]
        
        # Match against our translation string map, or build clean generic fallback string
        label_name = LOCALE_MAP.get(locale_code, f"{locale_code} (Regional Accent)")
        
        if label_name not in options:
            options[label_name] = {
                "lang": lang_code,
                "Female": [],
                "Male": []
            }
        
        if gender in ["Female", "Male"]:
            options[label_name][gender].append(short_name)
            
    # Alphabetize keys so drop-down menus appear highly organized
    return {k: options[k] for k in sorted(options.keys())}

# Initialize live system database footprint
VOICE_OPTIONS = load_all_voices()