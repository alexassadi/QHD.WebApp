import requests
import uuid
from decouple import config, Csv

API_KEY = config('ELEVEN_LABS_API_KEY')

VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
OUTPUT_FILE = "Audio/Test/test1.wav"

def generate_audio_file(text, voice_id):
    # Path to save generated audio
    unique_id = str(uuid.uuid4())[:8]
    AUDIO_FILE_PATH = f"C:/Users/aassa/Documents/Simon AI/Code/djangotutorial/static/fluent_audio_{unique_id}.mp3"

    URL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    # Headers for authentication
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # JSON payload
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",  # Model for English text-to-speech
        "voice_settings": {
            "stability": 0.5,  # Adjust voice stability (0.0 - 1.0)
            "similarity_boost": 0.8  # Adjust similarity boost (0.0 - 1.0)
        }
    }

    # Send request to ElevenLabs API
    response = requests.post(URL, json=data, headers=headers)

    # Check for errors
    if response.status_code == 200:
        return response.content  # return audio binary instead of saving to file
    else:
        raise Exception(f"Error generating audio: {response.status_code} - {response.text}")