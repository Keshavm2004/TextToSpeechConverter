import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
from deep_translator import GoogleTranslator
import asyncio
import edge_tts
import threading  # Fixes the UI freezing

# Initialize audio player engine
pygame.mixer.init()

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

class TTSApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Converter & Translator")
        self.root.geometry("540x620")
        
        # Alternating files completely eliminates Pygame/Windows file-locking crashes
        self.temp_files = ["preview_audio_A.mp3", "preview_audio_B.mp3"]
        self.current_file_idx = 0
        
        # UI Header
        ttk.Label(root, text="Text-to-Speech & Translator", font=("Helvetica", 14, "bold")).pack(pady=15)
        
        # Input Box Label
        ttk.Label(root, text="Type your text here (Any language):").pack(anchor="w", padx=25)
        self.text_box = tk.Text(root, height=8, width=58, font=("Helvetica", 10))
        self.text_box.pack(pady=5, padx=25)
        
        # Translation Toggle Checkbox Setup
        self.translate_var = tk.BooleanVar(value=True)
        self.translation_check = ttk.Checkbutton(
            root, 
            text="Translate text before speaking", 
            variable=self.translate_var, 
            command=self.toggle_translation
        )
        self.translation_check.pack(pady=5, padx=25, anchor="w")
        
        # Language/Accent Dropdown
        ttk.Label(root, text="Target Accent:").pack(anchor="w", padx=25, pady=(5, 0))
        self.language_var = tk.StringVar(value="English (United States)")
        self.language_menu = ttk.Combobox(root, textvariable=self.language_var, state="readonly")
        self.language_menu['values'] = list(VOICE_OPTIONS.keys())
        self.language_menu.pack(pady=5, padx=25, fill="x")

        # Voice Gender Dropdown
        ttk.Label(root, text="Voice Gender:").pack(anchor="w", padx=25, pady=(5, 0))
        self.gender_var = tk.StringVar(value="Female")
        self.gender_menu = ttk.Combobox(root, textvariable=self.gender_var, state="readonly")
        self.gender_menu['values'] = ["Female", "Male"]
        self.gender_menu.pack(pady=5, padx=25, fill="x")
        
        # Live Translation Preview Display Container
        ttk.Label(root, text="Translation Preview:", font=("Helvetica", 9, "bold")).pack(anchor="w", padx=25, pady=(10, 0))
        self.preview_label = ttk.Label(root, text="(Ready to translate)", font=("Helvetica", 10, "italic"), wraplength=450, foreground="gray")
        self.preview_label.pack(pady=5, padx=25, anchor="w")
        
        # Controls Dashboard Bar Frame
        self.controls_frame = ttk.Frame(root)
        self.controls_frame.pack(pady=15)        
        
        # Added object references to buttons so we can disable them during background loads
        self.speak_btn = ttk.Button(self.controls_frame, text="Speak", command=self.start_play_thread)
        self.speak_btn.grid(row=0, column=0, padx=5)
        ttk.Button(self.controls_frame, text="Pause", command=self.pause_audio).grid(row=0, column=1, padx=5)
        ttk.Button(self.controls_frame, text="Resume", command=self.resume_audio).grid(row=0, column=2, padx=5)
        ttk.Button(self.controls_frame, text="Stop", command=self.stop_audio).grid(row=0, column=3, padx=5)
        
        # Master Export Trigger Downloader Button
        self.download_btn = ttk.Button(root, text="Download Processed Audio (.mp3)", command=self.start_download_thread)
        self.download_btn.pack(pady=10)

    def toggle_translation(self):
        if self.translate_var.get():
            self.update_ui_text(self.preview_label, "(Ready to translate)", "gray")
        else:
            self.update_ui_text(self.preview_label, "(Translation turned off — will read original text)", "orange")

    def update_ui_text(self, label, text, color="black"):
        """Thread-safe UI text update helper."""
        self.root.after(0, lambda: label.config(text=text, foreground=color))

    def set_buttons_state(self, state):
        """Thread-safe UI interaction toggle helper."""
        self.root.after(0, lambda: self.speak_btn.config(state=state))
        self.root.after(0, lambda: self.download_btn.config(state=state))

    async def _async_generate_audio(self, text, voice, path):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)

    def generate_and_save_audio(self, target_path):
        """Runs in the background thread. No blocking operations touch the main GUI window anymore."""
        content = self.text_box.get("1.0", tk.END).strip()
        if not content:
            self.root.after(0, lambda: messagebox.showwarning("Input Required", "Please enter valid text to convert."))
            return False
            
        selected_accent = self.language_var.get()
        selected_gender = self.gender_var.get()
        
        voice_config = VOICE_OPTIONS[selected_accent]
        target_lang = voice_config["lang"]
        voice_name = voice_config[selected_gender]
        
        if self.translate_var.get():
            try:
                self.update_ui_text(self.preview_label, "Translating... Please wait.", "blue")
                processed_text = GoogleTranslator(source='auto', target=target_lang).translate(content)
                self.update_ui_text(self.preview_label, processed_text, "green")
            except Exception as e:
                self.update_ui_text(self.preview_label, "Translation failed.", "red")
                self.root.after(0, lambda: messagebox.showerror("Translation Error", f"Could not connect to translation service: {e}"))
                return False
        else:
            processed_text = content
            self.update_ui_text(self.preview_label, "(Translation bypassed)", "orange")
            
        try:
            self.update_ui_text(self.preview_label, "Generating Neural Voice... Please wait.", "blue")
            # Creates an isolated, thread-safe asynchronous event loop block inside this worker thread
            asyncio.run(self._async_generate_audio(processed_text, voice_name, target_path))
            self.update_ui_text(self.preview_label, processed_text, "green")
            return True
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("TTS Generation Error", f"Could not generate neural audio: {e}"))
            return False

    def start_play_thread(self):
        """Spawns background thread for processing to keep UI smooth."""
        self.set_buttons_state("disabled")
        threading.Thread(target=self._threaded_play, daemon=True).start()

    def _threaded_play(self):
        # 1. Safely disconnect old track from mixer memory
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        # 2. Swap temporary file assignments to eliminate potential lock races
        self.current_file_idx = 1 - self.current_file_idx
        active_temp_file = self.temp_files[self.current_file_idx]
        
        # 3. Generate file on background thread
        if self.generate_and_save_audio(active_temp_file):
            try:
                pygame.mixer.music.load(active_temp_file)
                pygame.mixer.music.play()
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Playback Error", f"Could not play audio file: {e}"))
        
        self.set_buttons_state("normal")

    def start_download_thread(self):
        """Spawns file selection window and saves data in a background thread."""
        target_path = filedialog.asksaveasfilename(
            defaultextension=".mp3", 
            filetypes=[("Audio Files", "*.mp3")]
        )
        if target_path:
            self.set_buttons_state("disabled")
            threading.Thread(target=self._threaded_download, args=(target_path,), daemon=True).start()

    def _threaded_download(self, target_path):
        if self.generate_and_save_audio(target_path):
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Audio file saved successfully to:\n{target_path}"))
        self.set_buttons_state("normal")

    def toggle_buttons_state(self, state):
         self.speak_btn.config(state=state)

    def pause_audio(self):
        pygame.mixer.music.pause()

    def resume_audio(self):
        pygame.mixer.music.unpause()

    def stop_audio(self):
        pygame.mixer.music.stop()

if __name__ == "__main__":
    window = tk.Tk()
    app = TTSApplication(window)
    window.mainloop()