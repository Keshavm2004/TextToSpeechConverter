import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
from deep_translator import GoogleTranslator
import asyncio
import edge_tts

from voices import VOICE_OPTIONS

# Initialize audio player engine
pygame.mixer.init()

class TTSApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Neural Presentation TTS")
        self.root.geometry("560x720") # Enlarged geometry layout window to host additions cleanly
        self.temp_filename = "preview_audio.mp3"
        
        # UI Header
        ttk.Label(root, text="Text-to-Speech & Translator Dashboard", font=("Helvetica", 14, "bold")).pack(pady=15)
        
        # Input Box Label
        ttk.Label(root, text="Type your presentation script here:").pack(anchor="w", padx=25)
        self.text_box = tk.Text(root, height=7, width=62, font=("Helvetica", 10))
        self.text_box.pack(pady=5, padx=25)
        
        # Translation Toggle Checkbox Setup
        self.translate_var = tk.BooleanVar(value=True)
        self.translation_check = ttk.Checkbutton(
            root, text="Translate text before speaking", 
            variable=self.translate_var, command=self.toggle_translation
        )
        self.translation_check.pack(pady=5, padx=25, anchor="w")
        
        # Target Layout Frame for Dropdowns
        dropdown_frame = ttk.Frame(root)
        dropdown_frame.pack(pady=5, padx=25, fill="x")
        
        # Language/Accent Dropdown
        ttk.Label(dropdown_frame, text="Target Accent:").grid(row=0, column=0, sticky="w", pady=2)
        self.language_var = tk.StringVar(value="English (United States)")
        self.language_menu = ttk.Combobox(dropdown_frame, textvariable=self.language_var, state="readonly")
        self.language_menu['values'] = list(VOICE_OPTIONS.keys())
        self.language_menu.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=(0, 5))
        self.language_menu.bind("<<ComboboxSelected>>", self.update_voice_variants)

        # Voice Gender Dropdown
        ttk.Label(dropdown_frame, text="Voice Gender:").grid(row=2, column=0, sticky="w", pady=2)
        self.gender_var = tk.StringVar(value="Female")
        self.gender_menu = ttk.Combobox(dropdown_frame, textvariable=self.gender_var, state="readonly")
        self.gender_menu['values'] = ["Female", "Male"]
        self.gender_menu.grid(row=3, column=0, sticky="ew", pady=(0, 10), padx=(0, 5))
        self.gender_menu.bind("<<ComboboxSelected>>", self.update_voice_variants)

        # NEW: Voice Variant Selector (Dynamic Choice Populator)
        ttk.Label(dropdown_frame, text="Voice Actor Style / Choice:").grid(row=2, column=1, sticky="w", pady=2)
        self.variant_var = tk.StringVar()
        self.variant_menu = ttk.Combobox(dropdown_frame, textvariable=self.variant_var, state="readonly")
        self.variant_menu.grid(row=3, column=1, sticky="ew", pady=(0, 10), padx=(5, 0))
        
        # Configure Grid Weights for side-by-side dropdown scaling layout equivalence
        dropdown_frame.columnconfigure(0, weight=1)
        dropdown_frame.columnconfigure(1, weight=1)

        # NEW: Speed Control Slider Configuration Layout
        ttk.Label(root, text="Speaker Pacing Rate (Speed Multiplier):", font=("Helvetica", 9, "bold")).pack(anchor="w", padx=25, pady=(5, 0))
        self.speed_slider = tk.Scale(
            root, from_=0.5, to=2.0, resolution=0.1, 
            orient="horizontal", length=450, background="#f0f0f0", troughcolor="#d9d9d9"
        )
        self.speed_slider.set(1.0) # Set standard normal default rate (1x speed)
        self.speed_slider.pack(pady=5, padx=25)
        
        # Live Translation Preview Display Container
        ttk.Label(root, text="Presentation Processing Log Preview:", font=("Helvetica", 9, "bold")).pack(anchor="w", padx=25, pady=(10, 0))
        self.preview_label = ttk.Label(root, text="(Ready to process text)", font=("Helvetica", 10, "italic"), wraplength=450, foreground="gray")
        self.preview_label.pack(pady=5, padx=25, anchor="w")
        
        # Controls Dashboard Bar Frame
        controls_frame = ttk.Frame(root)
        controls_frame.pack(pady=15)        
        ttk.Button(controls_frame, text="Speak", command=self.play_audio).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="Pause", command=self.pause_audio).grid(row=0, column=1, padx=5)
        ttk.Button(controls_frame, text="Resume", command=self.resume_audio).grid(row=0, column=2, padx=5)
        ttk.Button(controls_frame, text="Stop", command=self.stop_audio).grid(row=0, column=3, padx=5)
        
        # Master Export Trigger Downloader Button
        ttk.Button(root, text="Download Custom Audio Track (.mp3)", command=self.download_file).pack(pady=10)

        # Run primary initial update chain setup for variants configuration loop context
        self.update_voice_variants()

    def update_voice_variants(self, event=None):
        """Monitors selections and dynamically injects alternative choices per gender/accent."""
        selected_accent = self.language_var.get()
        selected_gender = self.gender_var.get()
        
        # Fetch the available list arrays from the database schema mappings 
        available_voices = VOICE_OPTIONS[selected_accent][selected_gender]
        
        # Generate clean user selection entries like: ['Voice 1', 'Voice 2']
        dropdown_labels = [f"Voice {i+1}" for i in range(len(available_voices))]
        self.variant_menu['values'] = dropdown_labels
        
        # Automatically fallback safe lock onto index element 0
        self.variant_menu.current(0)

    def toggle_translation(self):
        if self.translate_var.get():
            self.preview_label.config(text="(Ready to translate)", foreground="gray")
        else:
            self.preview_label.config(text="(Translation turned off — will read original text)", foreground="orange")

    async def _async_generate_audio(self, text, voice, path, rate_string):
        """Asynchronous helper modified to feed dynamic rate parameters to engine."""
        communicate = edge_tts.Communicate(text, voice, rate=rate_string)
        await communicate.save(path)

    def generate_and_save_audio(self, target_path):
        content = self.text_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Input Required", "Please enter valid text to convert.")
            return False
            
        selected_accent = self.language_var.get()
        selected_gender = self.gender_var.get()
        
        # Extract specific string element index selection matching our generated combo configurations
        variant_index = self.variant_menu.current()
        
        voice_config = VOICE_OPTIONS[selected_accent]
        target_lang = voice_config["lang"]
        voice_name = voice_config[selected_gender][variant_index]
        
        # Calculate EdgeTTS speed format constraint string conversion from Slider scale input
        # Example calculation: 1.5x -> (1.5 - 1.0) * 100 = +50%
        speed_multiplier = self.speed_slider.get()
        percentage_offset = int((speed_multiplier - 1.0) * 100)
        rate_string = f"+{percentage_offset}%" if percentage_offset >= 0 else f"{percentage_offset}%"
        
        if self.translate_var.get():
            try:
                self.preview_label.config(text="Translating... Please wait.", foreground="blue")
                self.root.update_idletasks()
                processed_text = GoogleTranslator(source='auto', target=target_lang).translate(content)
                self.preview_label.config(text=processed_text, foreground="green")
            except Exception as e:
                self.preview_label.config(text="Translation failed.", foreground="red")
                messagebox.showerror("Translation Error", f"Could not complete online translation: {e}")
                return False
        else:
            processed_text = content
            self.preview_label.config(text="(Translation bypassed)", foreground="orange")
            
        try:
            # Passes text, the specific voice model ID, destination path, and pacing constraints down to pipeline
            asyncio.run(self._async_generate_audio(processed_text, voice_name, target_path, rate_string))
            return True
        except Exception as e:
            messagebox.showerror("TTS Generation Error", f"Could not generate neural audio track pipeline: {e}")
            return False

    def play_audio(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        if self.generate_and_save_audio(self.temp_filename):
            try:
                pygame.mixer.music.load(self.temp_filename)
                pygame.mixer.music.play()
            except Exception as e:
                messagebox.showerror("Playback Error", f"Could not play audio file: {e}")

    def pause_audio(self):
        pygame.mixer.music.pause()

    def resume_audio(self):
        pygame.mixer.music.unpause()

    def stop_audio(self):
        pygame.mixer.music.stop()

    def download_file(self):
        target_path = filedialog.asksaveasfilename(
            defaultextension=".mp3", 
            filetypes=[("Audio Files", "*.mp3")]
        )
        if target_path:
            if self.generate_and_save_audio(target_path):
                messagebox.showinfo("Success", f"Audio file saved successfully to:\n{target_path}")

if __name__ == "__main__":
    window = tk.Tk()
    app = TTSApplication(window)
    window.mainloop()