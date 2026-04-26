"""Desktop AI live translator.

This app records short microphone chunks, uses Whisper to turn speech into
text, translates that text into English, and displays both the original speech
and translation in a CustomTkinter window.
"""

import os

# On macOS/Homebrew, some audio and FFmpeg tools may live in this folder.
# Adding it to PATH helps Whisper and audio libraries find those tools.
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

import sounddevice as sd
import whisper
from googletrans import Translator
import customtkinter as ctk
import numpy as np

# =========================
# CONFIG
# =========================
fs = 16000  # Sample rate in Hz. Whisper works well with 16 kHz audio.
duration = 1.5  # Number of seconds recorded in each microphone chunk.
target_lang = "en"  # Google Translate language code for English.
threshold = 0.01  # Minimum average audio volume needed to treat input as speech.

# App state. These values are changed by the Start/Stop buttons and audio loop.
running = False
buffer_text = ""

# =========================
# LOAD MODELS
# =========================
# Loading the model once at startup avoids reloading it for every audio chunk.
model = whisper.load_model("small")
translator = Translator()

# =========================
# UI CONFIG
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x500")
app.title("AI Live Translator")

# =========================
# HEADER
# =========================
title = ctk.CTkLabel(app, text="🌍 AI Live Translator",
                     font=("Arial", 28, "bold"))
title.pack(pady=15)

status = ctk.CTkLabel(app, text="Idle",
                      font=("Arial", 14))
status.pack(pady=5)

# =========================
# MAIN FRAME
# =========================
frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(padx=20, pady=20, fill="both", expand=True)

# Original
# Textbox that shows the speech recognized by Whisper before translation.
original_label = ctk.CTkLabel(frame, text="Original Speech",
                             font=("Arial", 14, "bold"))
original_label.pack(anchor="w", padx=10, pady=(10, 0))

original_text = ctk.CTkTextbox(frame, height=100)
original_text.pack(padx=10, pady=5, fill="x")

# Translation
# Textbox that shows the translated result returned by Google Translate.
translated_label = ctk.CTkLabel(frame, text="English Translation",
                               font=("Arial", 14, "bold"))
translated_label.pack(anchor="w", padx=10, pady=(10, 0))

translated_text = ctk.CTkTextbox(frame, height=100)
translated_text.pack(padx=10, pady=5, fill="x")

# =========================
# FUNCTIONS
# =========================
def is_speech(audio):
    """Return True when the recorded audio is loud enough to process.

    The microphone is always recording short chunks. This simple volume check
    skips quiet chunks so Whisper does not waste time transcribing silence.
    """
    return np.abs(audio).mean() > threshold


def process_audio():
    """Record, transcribe, translate, and update the UI for one audio chunk.

    Tkinter apps should not use an infinite while loop because that would freeze
    the interface. Instead, this function processes one chunk and schedules
    itself again with app.after(...) while the app is running.
    """
    global running, buffer_text

    if not running:
        return

    try:
        status.configure(text="Listening...", text_color="green")

        # Record one short chunk from the default microphone.
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()

        # Skip quiet input and quickly schedule the next listening pass.
        if not is_speech(audio):
            if running:
                app.after(100, process_audio)
            return

        status.configure(text="Processing...", text_color="yellow")

        # Whisper expects a 1D audio array, so flatten the microphone recording.
        result = model.transcribe(audio.flatten())
        text = result["text"].strip()

        # Very short results are usually noise or partial recognition.
        if len(text) < 3:
            if running:
                app.after(100, process_audio)
            return

        # Keep a small rolling history in case future features need context.
        buffer_text += " " + text
        buffer_text = buffer_text[-200:]

        # Translate only the latest chunk. The destination can be changed in CONFIG.
        translated = translator.translate(text, dest=target_lang)

        # Replace the textboxes with the newest original text and translation.
        original_text.delete("1.0", "end")
        original_text.insert("end", text)

        translated_text.delete("1.0", "end")
        translated_text.insert("end", translated.text)

    except Exception as e:
        # Surface errors in the app instead of crashing the whole UI.
        original_text.delete("1.0", "end")
        original_text.insert("end", f"Error: {str(e)}")

    # Schedule the next chunk after a short pause so the UI remains responsive.
    if running:
        app.after(100, process_audio)


def start_listening():
    """Start the microphone processing loop."""
    global running
    if not running:
        running = True
        process_audio()


def stop_listening():
    """Stop processing new microphone chunks."""
    global running
    running = False
    status.configure(text="Stopped", text_color="red")


# =========================
# BUTTONS
# =========================
button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=10)

start_btn = ctk.CTkButton(button_frame, text="Start",
                          command=start_listening)
start_btn.pack(side="left", padx=10)

stop_btn = ctk.CTkButton(button_frame, text="Stop",
                         command=stop_listening,
                         fg_color="red")
stop_btn.pack(side="right", padx=10)

# =========================
# RUN APP
# =========================
app.mainloop()
