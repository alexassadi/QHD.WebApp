import base64
import json
import requests
from datetime import datetime
import uuid
from decouple import config,Csv

API_KEY = config('LANGUAGE_CONFIDENCE_API_KEY')

AUDIO_FILE = "Audio/Test/test1.mp3"

def generate_pronunciation_score(audio_file, expected_text, speaker_gender, speaker_age, resultid=None):
    # Read and convert the audio file to Base64

    url = "https://apis.languageconfidence.ai/pronunciation/uk"

    payload = json.dumps({
    "audio_base64": audio_file,
    "audio_format": "mp3",
    "expected_text": expected_text,
    "user_metadata": {'speaker_gender': speaker_gender,
                        'speaker_age': speaker_age}
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'api-key': API_KEY
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json()


    result["resultid"] = resultid    
    result["timestamp"] = datetime.now().isoformat()

    json_result = json.dumps(result)

    return json_result