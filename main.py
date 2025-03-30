import openai_func as oa
import elevenlabs_func as el
import languageconfidence_func as lc
import s3_func as s3
from pathlib import Path

cefr_level = 'B2'
subject = 'DEVELOP'
quantity = 3

runid = 'test3'

voice_id = "EXAVITQu4vr4xnSDxMaL"

speaker_gender = 'female'
speaker_age = 'adult'

root_audio_directory = f'Audio/Test/{runid}'

directory_path = Path(root_audio_directory)

# Create directory if it doesn't exist
directory_path.mkdir(parents=True, exist_ok=True)

sentences = oa.initial_prompt(cefr_level, subject, quantity)

count = 1

for sentence in sentences:
    audio_path = f"{root_audio_directory}/{runid}-{count}.mp3"

    el.generate_audio_file(sentence, voice_id, audio_path)

    resultid = f"{runid}-{count}"

    json_result, uid = lc.generate_pronunciation_score(audio_path, sentence, speaker_gender, speaker_age, resultid)

    s3_bucket = 'qhd-speech-training'
    s3_key = f'test/test_results/runid={runid}/{uid}.json'

    s3.export_result_to_s3(s3_bucket, s3_key, json_result)

    count += 1