# AI Live Translator
A real-time AI system that converts multilingual speech into English subtitles with a modern desktop interface.
A desktop app that listens to speech from your microphone, converts it to text
with Whisper, translates it into English, and shows both results in a simple UI.

## Features

- Records short microphone chunks
- Detects when the input is loud enough to process
- Transcribes speech with Whisper
- Translates the recognized text to English
- Displays original speech and translated text in a CustomTkinter window
- Includes Start and Stop controls

## Tech Stack

- Python
- OpenAI Whisper for speech recognition
- Google Translate through `googletrans`
- CustomTkinter for the desktop UI
- SoundDevice for microphone recording
- NumPy for basic audio volume checking

## Project Structure

```text
.
├── live.py           # Main application code
├── requirements.txt  # Python dependencies
├── readme.md         # Project documentation
└── temp.wav          # Optional/generated audio file, ignored by Git
```

## How It Works

1. The user clicks `Start`.
2. The app records a 1.5-second audio chunk from the microphone.
3. A simple volume check skips quiet chunks.
4. Whisper transcribes the audio chunk into text.
5. Google Translate translates that text into English.
6. The UI shows the original recognized speech and the English translation.
7. The app schedules the next audio chunk while it is still running.

This is chunk-based processing, not true continuous streaming. That means there
can be a small delay between speaking and seeing the translated text.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python live.py
```

## Notes

- On macOS, allow microphone access when the system asks for permission.
- Whisper may need FFmpeg installed on your machine.
- The app currently translates to English because `target_lang = "en"` in
  `live.py`.
- Accuracy depends on microphone quality, background noise, and speaker clarity.

## Limitations

- Uses short chunks instead of real streaming audio
- Works best with one speaker at a time
- Uses a simple volume threshold to detect speech
- Internet access may be needed for translation through `googletrans`

## Future Improvements

- Add a language selector in the UI
- Add true streaming transcription
- Show more transcript history
- Add support for multiple speakers
- Add export or copy buttons for translated text
