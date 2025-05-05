import os
import time
import json
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
from elevenlabs import ElevenLabs
from google import genai
from google.genai import types
from pydub import AudioSegment
import simpleaudio as sa
import tempfile

#Load API keys

load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
eleven = ElevenLabs(api_key=ELEVEN_API_KEY)


# Voice settings

SAMPLE_RATE = 16000
TRIGGER_WORDS = ["virgo", "vergo", "burgo", "vir go"]
VOSK_MODEL_PATH = "model"
SILENCE_THRESHOLD = 1500
SILENCE_DURATION = 0.5
MAX_RECORD_DURATION = 15



#Gemini settings
GEMINI_MAX_OUTPUT_TOKEN=100
GEMINI_INSTRUCTION = "Your name is Virgo and you only response in short answer very direct to the point, but you are very intelligent ang knowlegable."



#Load vosk
vosk_model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE, json.dumps(TRIGGER_WORDS))

#Voice activity detection
def is_speech(frame_bytes, threshold=SILENCE_THRESHOLD):
    audio = np.frombuffer(frame_bytes, dtype=np.int16).astype(np.float32)
    rms = np.sqrt(np.mean(audio ** 2))
    return rms > threshold

#Record audio until silent

def record_voice():
    print("Virgo:\nSpeak now... (auto-stop on silence)\n")
    buffer = []
    start_time = time.time()
    silence_start = None

    def callback(indata, frames, time_info, status):
        nonlocal silence_start, start_time
        frame = bytes(indata)
        buffer.append(frame)

        if is_speech(frame):
            silence_start = None
        else:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > SILENCE_DURATION:
                raise sd.CallbackStop()

        elapsed = time.time() - start_time
        if elapsed > MAX_RECORD_DURATION - 2:
            print("Virgo:Still listening... (about to stop)")

        if elapsed > MAX_RECORD_DURATION:
            raise sd.CallbackStop()


    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        try:
            sd.sleep(int(MAX_RECORD_DURATION * 1000))
        except sd.CallbackStop:
            pass

    print("Done recording.")
    raw_audio = b''.join(buffer)
    audio_array = np.frombuffer(raw_audio, dtype=np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        wav_path = tmpfile.name
        write(wav_path, SAMPLE_RATE, audio_array)
        return wav_path


# Pass gemini to elevenlabs convert mp3 to wav and play using ffmpeg
def elevenlabs_speech(text):
    try:
        # Get audio as generator
        audio_stream = eleven.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            text=text
        )

        # Collect bytes from generator
        audio_data = b''.join(chunk for chunk in audio_stream)

        # Save MP3
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_file:
            mp3_file.write(audio_data)
            mp3_path = mp3_file.name

        # Convert to WAV
        wav_path = mp3_path.replace(".mp3", ".wav")
        os.system(f"ffmpeg -y -loglevel error -i {mp3_path} {wav_path}")

        # Play audio
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        # Clean up
        os.remove(mp3_path)
        os.remove(wav_path)

    except Exception as e:
        print("Virgo: playback error ", e)



#Gemini
def the_gemini(prompt_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_INSTRUCTION,
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKEN,
                temperature=0.1
            )
        )
        reply = response.text.strip()
        print("Virgo says:\n" + reply)
        elevenlabs_speech(reply)
        return reply
    except Exception as e:
        print("Virgo: Error", e)
        return ""

#Full voice interaction
def handle_trigger():
    wav_path = record_voice()
    try:
        with open(wav_path, "rb") as f:
            response = eleven.speech_to_text.convert(
                model_id="scribe_v1",
                file=f,
                language_code="en"
            )
            transcript = response.text.strip()
            print("You said:", transcript)
            if transcript:
                the_gemini(transcript)
    except Exception as e:
        print("Virgo: STT error", e)
    finally:
        os.remove(wav_path)



#Detect live listening via Vosk
def vosk_listen(indata, frames, time_info, status):
    audio = bytes(indata)
    if recognizer.AcceptWaveform(audio):
        result = json.loads(recognizer.Result())
        spoken = result.get("text", "").lower()
        print(f"Virgo heard: {spoken}")
        if any(word in spoken for word in TRIGGER_WORDS):
            handle_trigger()




#Continuous listening
def listen_for_trigger():
    print("Say 'Virgo' to speak")
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=vosk_listen):
        while True:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        listen_for_trigger()
    except KeyboardInterrupt:
        print("\nVirgo: Good bye!")
