import json
import base64
from django.shortcuts import render, redirect
from .forms import SentenceGenerationForm, PronunciationForm, PracticeForm
import sys
import os
from pathlib import Path
import subprocess
from .models import Sentence
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import re
from collections import defaultdict
import random
import uuid
from django.core.files.storage import default_storage
import requests
from django.core.files.base import ContentFile
from decouple import config
import tempfile
import traceback

# Add the utilities folder (2 levels up) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import from multiple files
import openai_func as oa
import elevenlabs_func as el
import languageconfidence_func as lc
import s3_func as s3

# OpenAI API Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY')
ELEVENLABS_API_KEY = config('ELEVEN_LABS_API_KEY')
LANGUAGECONFIDENCE_API_KEY = config('LANGUAGE_CONFIDENCE_API_KEY')

MP3_FILEPATH = None

def generate_sentences(request):
    sentences = []  # Stores final API results for display

    if request.method == 'POST':
        form = SentenceGenerationForm(request.POST)
        print("🚀 Form submission detected!")

        if form.is_valid():
            print("✅ Form data is valid")
            # Extract data from form
            quantity = form.cleaned_data['sentence_number']
            vocab_list = form.cleaned_data['vocab_list']

            # 1. OpenAI API Request
            print(vocab_list, quantity)
            while len(sentences) == 0:
                sentences = oa.initial_prompt(vocab_list, quantity)
            print(sentences)

            for sentence in sentences:
                Sentence.objects.create(text=sentence)

    else:
        form = SentenceGenerationForm()

    return render(request, 'apiapp/generate_sentences.html', {'form': form, 'sentences': sentences})

import random  # Import to pick random sentences

def practice_view(request):
    form = PracticeForm()
    score = None
    selected_sentence = None
    fluent_audio_path = None
    show_speaker_gender = False
    uid = None

    # Track progress (total = 5 sentences)
    if 'exercise_sentences' not in request.session:
        all_sentences = list(Sentence.objects.all())
        random.shuffle(all_sentences)
        request.session['exercise_sentences'] = [s.id for s in all_sentences[:5]]
        request.session['progress'] = 0  # Start at 0
        request.session['show_recording_frame'] = False
        request.session['ready_for_next_sentence'] = False
        request.session['cached_audio_path'] = None

    # Retrieve the current sentence from progress
    sentence_ids = request.session['exercise_sentences']
    progress = request.session['progress']

    # Check if progress is complete
    if progress >= len(sentence_ids):
        return redirect('completion_page')  # Redirect to success/completion page

    # Retrieve the next sentence
    try:
        selected_sentence = Sentence.objects.get(id=sentence_ids[progress])
        match = re.search(r'\b[A-Z]{2,}\b', selected_sentence.text)
        key_term = match.group(0) if match else "Other"

        # Bold the key term inside the sentence
        highlighted_sentence = selected_sentence.text.replace(key_term, f"<strong>{key_term}</strong>")

        if request.session.get('cached_audio_path') is None:
            audio_data = el.generate_audio_file(selected_sentence.text, 'EXAVITQu4vr4xnSDxMaL')

            # Upload to S3 using default_storage
            key = f"audio/fluent_audio/fluent_{uuid.uuid4().hex}.mp3"
            fluent_audio_path = s3.export_result_to_s3(key, audio_data, 'audio/mpeg')

            request.session['cached_audio_path'] = fluent_audio_path
        else:
            fluent_audio_path = request.session['cached_audio_path']  # ✅ Use cached audio file

        # Track if the user has listened once
        if 'show_recording_frame' not in request.session:
            request.session['show_recording_frame'] = False
        if 'ready_for_next_sentence' not in request.session:
            request.session['ready_for_next_sentence'] = False

        # Show recording and listen again after listening finishes
        if 'listen_action' in request.POST:
            request.session['show_recording_frame'] = True
            request.session['ready_for_next_sentence'] = True
            request.session.modified = True  # Force Django to save session changes

        # Only move forward if the "Next Sentence" button is pressed
        if 'next_sentence' in request.POST:
            request.session['progress'] += 1
            request.session['show_recording_frame'] = False
            request.session['ready_for_next_sentence'] = False
            request.session['cached_audio_path'] = None
            request.session.modified = True  # ✅ Force session to save
            return redirect('practice')  # ✅ Redirect to refresh the sentence display

    except Sentence.DoesNotExist:
        selected_sentence = None
        key_term = "Unknown"
        highlighted_sentence = ""


    return render(request, 'apiapp/practice.html', {
        'sentence': selected_sentence,
        'key_term': key_term,
        'fluent_audio_path': fluent_audio_path,
        'progress': progress + 1,
        'total_sentences': len(sentence_ids),
        'show_recording_frame': request.session.get('show_recording_frame', False),
        'ready_for_next_sentence': request.session.get('ready_for_next_sentence', False),
        'score': score
    })

def reset_progress(request):
    # Reset progress to zero
    request.session['progress'] = 0

    # Select 5 new random sentences
    all_sentences = list(Sentence.objects.all())
    random.shuffle(all_sentences)
    request.session['exercise_sentences'] = [s.id for s in all_sentences[:5]]

    request.session['show_recording_frame'] = False
    request.session['ready_for_next_sentence'] = False

    request.session['cached_audio_path'] = None

    # Redirect back to the practice page
    return redirect('practice')

def completion_page(request):
    return render(request, 'apiapp/completion.html')

def save_and_process_audio(request):
    print("🔔 Entered save_and_process_audio view")

    if request.method == 'POST':
        print("🎧 Received audio POST request.")
        try:
            audio_base64 = request.POST.get('audio_file')
            sentence_id = request.POST.get('sentence_id')
            print(f"🔍 Received sentence ID: {sentence_id}")

            # ✅ Confirm data is received
            if not audio_base64:
                print("❌ No audio data received.")
                return JsonResponse({'success': False, 'error': 'No audio data received.'}, status=400)

            # Create a ContentFile from the base64-decoded audio
            audio_binary = base64.b64decode(audio_base64)

            unique_id = uuid.uuid4().hex
            original_key = f"audio/recordings/recording_{unique_id}.mp3"
            converted_key = f"audio/recordings/converted_{unique_id}.mp3"

            # Save original audio to S3
            s3_url = s3.export_result_to_s3(original_key, audio_binary, content_type='audio/mpeg')

            # Save original to temp file (for ffmpeg conversion)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as original_temp:
                original_temp.write(audio_binary)
                original_path = original_temp.name

            # Convert using ffmpeg to new temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as converted_temp:
                converted_path = converted_temp.name

            try:
                print("SCORING AUDIO")
                try:
                    subprocess.run([
                        "ffmpeg", 
                        "-y",
                        "-i", original_path,
                        "-ar", "48000",
                        "-ac", "1",
                        "-b:a", "192k",
                        converted_path
                    ], check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    print("❌ FFMPEG failed!")
                    print("STDERR:", e.stderr)
                    print("STDOUT:", e.stdout)
                    raise

                # Read and re-encode converted file
                with open(converted_path, "rb") as f:
                    converted_audio_binary = f.read()

                # Save converted audio to S3
                converted_url = s3.export_result_to_s3(converted_key, converted_audio_binary, content_type='audio/mpeg')

                # Encode to base64 for LC
                converted_audio_base64 = base64.b64encode(converted_audio_binary).decode("utf-8")

                # Get sentence
                sentence = Sentence.objects.get(id=sentence_id)

                # Score with Language Confidence
                result_json = lc.generate_pronunciation_score(
                    converted_audio_base64, sentence.text, 'male', 'adult'
                )
                score_data = json.loads(result_json)
                score = score_data["overall_score"]

                # ✅ Extract and sort lowest scoring words
                sorted_words = sorted(score_data["words"], key=lambda x: x["word_score"])
                lowest_words = [word["word_text"] for word in sorted_words[:3]]
                print(lowest_words)

                underlined_sentence = sentence.text
                for word in lowest_words:
                    underlined_sentence = underlined_sentence.replace(f' {word} ', f"<span class='clickable-word' data-word='{word}'> <u>{word}</u> </span>", 1)

                return JsonResponse({
                    'success': True,
                    'score': score,
                    'underlined_sentence': underlined_sentence,
                    'audio_url': converted_url
                })

                
            except Sentence.DoesNotExist:
                print("ERROR SCORING AUDIO")
                score = "Error: Sentence not found."

            print(f"✅ Audio successfully saved at: {converted_url}")
            return JsonResponse({
                'success': True,
                'score': score
            })

        except Exception as e:
            print(f"❌ Error in save_audio view: {e}")
            traceback.print_exc()  # This prints the full error trace to the console
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
    print("🚫 Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

def submit_recording(request):
    if request.method == 'POST':
        base64_audio = request.POST.get('recording_audio_base64')
        print("POST RECEIVED")
        print(base64_audio)

        if base64_audio:
            print("✅ Received Base64 Audio (First 50 chars):", base64_audio[:50])
            
            # Optional: Save the Base64 data as an MP3 file
            import base64
            from django.conf import settings
            import os

            # Decode and save as MP3
            audio_data = base64.b64decode(base64_audio)
            filename = f"recordings/recording_from_base64_{uuid.uuid4().hex}.mp3"
            audio_content = ContentFile(audio_data)
            s3_path = default_storage.save(filename, audio_content)
            audio_url = default_storage.url(s3_path)

            return JsonResponse({'success': True, 'file_path': audio_url})
        else:
            return JsonResponse({'success': False, 'error': 'No audio data received'})
        
def generate_word_audio(request):
    if request.method == 'POST':
        word = request.POST.get('word')

        if not word:
            return JsonResponse({'success': False, 'error': 'No word provided.'}, status=400)

        try:
            # ✅ Generate the MP3 file
            audio_b64 = el.generate_audio_file(word, 'EXAVITQu4vr4xnSDxMaL')

            s3_key = f'audio/words/word_{uuid.uuid4().hex}.mp3'

            # ✅ Return the URL for playback
            audio_url = s3.export_result_to_s3(s3_key, audio_b64, 'audio/mpeg')
            return JsonResponse({'success': True, 'audio_url': audio_url})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

import subprocess

def debug_static(request):
    output = subprocess.check_output("find staticfiles/ -name '*.css'", shell=True).decode()
    return HttpResponse(f"<pre>{output}</pre>")