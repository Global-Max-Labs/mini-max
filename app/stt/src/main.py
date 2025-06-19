# import config
import whisper
import torch
import numpy as np
import ffmpeg
import io
import pyaudio
import time
import webrtcvad
import pyttsx3
import requests
import subprocess
import threading
import asyncio
import sounddevice as sd

wake_words = {
    "mini max": "Mini Max",
    "alfred": "Alfred",
    "minimax": "Mini Max",
    "mini macs": "Mini Max",
    "Minnie Max": "Mini Max",
    "Minnie Max": "Mini Max",
    "Many max": "Mini Max",
    "Mini Mac": "Mini Max",
    "Mini Mac": "Mini Max",
    "Mini-Max": "Mini Max",
    "Mini-Mac": "Mini Max",
    "MiniMac": "Mini Max",
    # Add more wake words as needed
}


def play_tone(frequency=440, duration=1.0, samplerate=44100):
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(wave, samplerate)
    sd.wait()


async def set_timer_with_tone(seconds):
    print(f"Timer set for {seconds} seconds.")
    await asyncio.sleep(seconds)
    print("Time's up!")
    play_tone()


async def set_new_timer(seconds):
    # Start the timer
    asyncio.create_task(set_timer_with_tone(seconds))


def play_video(video_filename):
    #python subprocess to play video
    print('starting subprocess')
    process = subprocess.Popen(
        ["ffplay", "-autoexit", f"./assets/{video_filename}.mp4"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )


def show_text_file(text_filename):
    process = subprocess.Popen(["open", f"./assets/{text_filename}.txt"])


def trigger_action(action):
    if action == "play_cutting_shallots":
        print('playing cutting shallots')
        threading.Thread(target=play_video, args=["cutting_shallots"], daemon=True).start()
    elif action == "play_cutting_mushrooms":
        threading.Thread(target=play_video, args=["cutting_mushrooms"], daemon=True).start()
    elif action == "show_veloute":
        threading.Thread(target=show_text_file, args=["veloute"], daemon=True).start()
    return None


engine = pyttsx3.init()

# change voice to male
voices = engine.getProperty('voices')
for voice in voices:
    if voice in voices:
        # print(voice.gender)
        # print(voice.languages)
        if voice.languages == ["en_GB"] and voice.name == "Daniel":
            print(voice)
        #     print(voice.gender)
            engine.setProperty('voice', voice.id)
            # engine.say("Hello, I am Alfred. How can I help you today sir?")
            # engine.runAndWait()

print('loading model...')
model = whisper.load_model("base")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # check if GPU is available
model.to(device)  # move model to device (GPU or CPU)
print('model loaded!')
def exact_div(x, y):
    assert x % y == 0
    return x // y

# hard-coded audio hyperparameters
SAMPLE_RATE = 16000
N_FFT = 400
N_MELS = 80
HOP_LENGTH = 160
CHUNK_LENGTH = 30
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE  # 480000: number of samples in a chunk
N_FRAMES = exact_div(N_SAMPLES, HOP_LENGTH)  # 3000: number of frames in a mel spectrogram input
CHUNK_SIZE = 480
# CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
CAPTURE_DURATION = 5  # seconds
# VAD_THRESHOLD = 0.01
VAD_THRESHOLD = 200
VAD_MODE = 3
VAD_SILENCE_LENGTH = 1000  # milliseconds

# Create a VAD object with the desired mode
vad = webrtcvad.Vad(VAD_MODE)


def load_audio_stream(stream, sr: int = SAMPLE_RATE):
    """
    Read an audio stream as mono waveform, resampling as necessary
    Parameters
    ----------
    stream: io.BytesIO
        The audio stream to read
    sr: int
        The sample rate to resample the audio if necessary
    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input("pipe:0", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True, input=stream.read())
        )
        print('audio loaded!')
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


def start_audio_stream():
    # Create an instance of PyAudio
    pa = pyaudio.PyAudio()

    # Open a microphone stream
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    # Create a bytes buffer to hold the audio data
    audio_buffer = io.BytesIO()

    silence_start_time = None
    while True:
        data = stream.read(CHUNK_SIZE)
        # Check if there is speech activity in the current chunk
        is_speech = vad.is_speech(data, SAMPLE_RATE)
        if is_speech:
            silence_start_time = None
            # Write the audio data to the current audio buffer
            audio_buffer.write(data)
        # If there is no speech activity and we are not already in a silence period, start a new one
        elif silence_start_time is None:
            silence_start_time = time.monotonic()
        # If there is no speech activity and we are in a silence period, check if the period is long enough
        elif time.monotonic() - silence_start_time > VAD_SILENCE_LENGTH / 1000:
            # If the silence period is long enough, assume the current audio buffer is complete
            if audio_buffer.tell() > 0:
                print("End of speech detected")
                # Stop capturing and clean up
                break

    stream.stop_stream()
    stream.close()
    pa.terminate()
    # Reset the buffer position to the beginning
    audio_buffer.seek(0)
    return audio_buffer


def run_listener():
    while True:
        print('starting audio stream...')
        new_stream = start_audio_stream()
        print("loading audio...")
        audio = load_audio_stream(new_stream)
        print("processing audio...")
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        options = whisper.DecodingOptions(language= 'en', fp16=False)

        print("decoding...")

        with torch.no_grad():  # disable gradient tracking for efficiency
            result = whisper.decode(model, mel, options)

        print("processing...")

        if result.no_speech_prob < 0.5:
            print(result.text)

            # Check for any wake word in the text
            detected_wake_word = None
            for wake_word, assistant_name in wake_words.items():
                if wake_word.lower() in result.text.lower():
                    detected_wake_word = wake_word
                    assistant_identity = assistant_name
                    break

            if detected_wake_word:
            # if detected_wake_word:
                # Remove the wake word from the text
                text = result.text.lower().replace(detected_wake_word, "").strip()
                print(f"Wake word '{detected_wake_word}' detected. Assistant identity: {assistant_identity}")
                print(f"Input Text: {text}")

                data = {"space": "chatbot", "content": text}
                resp = requests.post("http://localhost:8000/api/text/chat/", json=data)
                print(resp.json())
                if resp.json()["answer"] != "Please connect me to bubble network":
                    if "action" in resp.json() and resp.json()["action"] != "":
                        print(resp.json()["action"],' triggering this action')
                        trigger_action(resp.json()["action"])
                    else:
                        engine.say(resp.json()["answer"])
                        engine.runAndWait()
                else:
                    engine.say("I have no idea what you are saying. Use your batman voice")
                    engine.runAndWait()


if __name__ == "__main__":
    run_listener()
