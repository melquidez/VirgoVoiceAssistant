# Virgo Voice Assistant (Python)

### This project demonstrates how to combine multiple approaches by integrating local tools and commercial APIs into a unified voice assistant.



An intelligent voice assistant powered by:
- Real-time hotword detection using [Vosk](https://alphacephei.com/vosk/)
- Smart AI replies via [Gemini 2.0 Flash](https://ai.google.dev/)
- Speech recognition & text-to-speech by [ElevenLabs](https://elevenlabs.io/)
- Fully functional on Linux using FFmpeg and Python

---

## Features

- Say "Virgo" to activate
- Records your voice until you stop speaking (max within 15 sec or silence detected)
- Transcribes your voice using ElevenLabs STT
- Sends it to Gemini AI for a reply
- Speaks the response back with ElevenLabs TTS

---

## Requirements

- Python 3.10+
- Linux (tested on Kali, Ubuntu)
- Working microphone

### Python dependencies

Install all with:

```bash
pip install -r requirements.txt
```

**OR manually:**

```bash
pip install sounddevice scipy python-dotenv vosk elevenlabs google-genai pydub simpleaudio
sudo apt install ffmpeg
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/virgo-voice-assistant.git
cd virgo-voice-assistant
```

### 2. Set up `.env`

Create a `.env` file with your API keys:

```ini
ELEVEN_API_KEY=your_elevenlabs_key
GEMINI_API_KEY=your_gemini_key
```

### 3. Download a Vosk model

You need to download the English model and extract it into a folder named `model/`:

```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model
```

---

## Usage

Run the assistant:

```bash
python voice_assistant.py
```

Then just say:

```
Virgo
```

And the assistant will listen and speak!

---

## Exiting

Press `Ctrl+C` anytime to stop the assistant gracefully.

---

---

## TODO

- [ ] Connect to esp32 dev board

---

## Credits

- [Vosk](https://github.com/alphacep/vosk-api)
- [ElevenLabs API](https://elevenlabs.io/)
- [Google Gemini](https://ai.google.dev/)
- FFmpeg, Pydub, SimpleAudio

---




## License

MIT — free to use, modify, and share.
