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

def practice_view(request):
    score_data = None
    selected_sentence = None
    fluent_audio_path = None
    show_speaker_gender = False
    uid = None
    grouped_sentences = defaultdict(list)

    # Extract sentences and group by key term (capitalized word)
    sentences = Sentence.objects.all()
    for sentence in sentences:
        match = re.search(r'\b[A-Z]{2,}\b', sentence.text)  # Detect capitalized word
        key_term = match.group(0) if match else "Other"
        grouped_sentences[key_term].append(sentence)

    # Clear session data only if `reset_page=true` is detected (Page Refresh)
    if request.GET.get('reset_page') == 'true':
        request.session.clear()
        print("🔄 Page refreshed — Session data cleared")
        return JsonResponse({'status': 'reset'})

    if 'selected_sentence_id' in request.session:
        try:
            selected_sentence = Sentence.objects.get(id=request.session['selected_sentence_id'])
            fluent_audio_path = request.session.get('fluent_audio_path')
            show_speaker_gender = True
        except Sentence.DoesNotExist:
            selected_sentence = None

    # Handle Pronunciation Submission
    if request.method == 'POST':
        form = PronunciationForm(request.POST, request.FILES)

        if 'sentence' in request.POST and 'speaker_gender' not in request.POST:
            if form.is_valid():
            # Correctly retrieve sentence ID for the form
                sentence_id = request.POST.get('sentence')
                try:
                    selected_sentence = Sentence.objects.get(id=sentence_id)
                except Sentence.DoesNotExist:
                    selected_sentence = None

                if selected_sentence:
                    selected_sentence = form.cleaned_data['sentence']
                    fluent_audio_path = el.generate_audio_file(selected_sentence.text, 'EXAVITQu4vr4xnSDxMaL')

                    uid = fluent_audio_path.split('_')[-1][:-4]

                    if 'audio_files' not in request.session:
                        request.session['audio_files'] = []
                    request.session['audio_files'].append(fluent_audio_path)

                    print(f"✅ Fluent audio file generated: {fluent_audio_path}")
                    show_speaker_gender = True  # Show the speaker gender field after sentence selection
                    form = PronunciationForm(initial={'sentence': selected_sentence.id})

        elif 'speaker_gender' in request.POST:
            print("🔎 Speaker gender selection process started")
            if form.is_valid():
                print("✅ Form data is valid")
                selected_sentence = form.cleaned_data['sentence']
                speaker_gender = form.cleaned_data['speaker_gender']
                audio_base64 = form.cleaned_data['audio_file']
                #print(audio_base64)

                # Decode Base64 back into MP3 file
                mp3_data = base64.b64decode(audio_base64)
                mp3_file_path = f"static/recording_{uid}.mp3"

                # Save MP3 file for debugging (optional)
                with open(mp3_file_path, "wb") as mp3_file:
                    mp3_file.write(mp3_data)

                request.session['audio_files'].append(mp3_file_path)

                subprocess.run([
                    "ffmpeg", "-i", mp3_file_path,
                    "-ar", "48000",       # Higher sample rate
                    "-ac", "1",           # Mono audio for clarity
                    "-b:a", "192k",       # Higher bitrate for improved sound
                    f"converted_audio_{uid}.mp3"
                ], check=True)

                request.session['audio_files'].append(f"converted_audio_{uid}.mp3")

                with open(f"converted_audio_{uid}.mp3", "rb") as audio:
                        audio_base64 = base64.b64encode(audio.read()).decode("utf-8")
                

                # Send uploaded audio to LanguageConfidence API for scoring
                print("🟩 Sending Data to API:", score_data)
                json_result, uid  = lc.generate_pronunciation_score(audio_base64, selected_sentence.text, speaker_gender, 'adult')

                score_data = json.loads(json_result)

                request.session['delete_audio_after_score'] = True
                
            else:
                print("❌ Form data is invalid:", form.errors)

    else:
        form = PronunciationForm()

    if request.session.get('delete_audio_after_score'):
        if 'audio_files' in request.session:
            for file_path in request.session['audio_files']:
                full_path = os.path.join(settings.BASE_DIR, file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"🗑️ Deleted audio file: {full_path}")
            request.session.pop('audio_files', None)
            request.session.pop('delete_audio_after_score', None)

    return render(request, 'apiapp/practice.html', {
        'sentence': selected_sentence,
        
        'form': form,
        'score_data': score_data,
        'fluent_audio_path': fluent_audio_path,
        'show_speaker_gender': show_speaker_gender,
        'grouped_sentences': dict(grouped_sentences)
    })


import random  # Import to pick random sentences

def practice_view2(request):
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
            return redirect('practice2')  # ✅ Redirect to refresh the sentence display

    except Sentence.DoesNotExist:
        selected_sentence = None
        key_term = "Unknown"
        highlighted_sentence = ""


    return render(request, 'apiapp/practice2.html', {
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
    return redirect('practice2')

def completion_page(request):
    return render(request, 'apiapp/completion.html')

def save_audio(request):
    if request.method == 'POST':
        try:
            audio_base64 = request.POST.get('audio_file')
            sentence_id = request.POST.get('sentence_id')

            # ✅ Confirm data is received
            if not audio_base64:
                print("❌ No audio data received.")
                return JsonResponse({'success': False, 'error': 'No audio data received.'}, status=400)

            # ✅ Ensure STATIC_ROOT is defined
            if not settings.STATIC_ROOT:
                print("❌ STATIC_ROOT is not defined.")
                return JsonResponse({'success': False, 'error': 'STATIC_ROOT is not defined.'}, status=500)

            # ✅ Generate a unique filename
            unique_filename = f"recording_{uuid.uuid4().hex}.mp3"

            # Create a ContentFile from the base64-decoded audio
            audio_content = ContentFile(base64.b64decode(audio_base64))

            # Save it to S3
            s3_path = default_storage.save(unique_filename, audio_content)

            # Get the public URL
            public_url = default_storage.url(s3_path)

            # ✅ Define file path in static storage
            file_path = os.path.join('recordings', unique_filename)
            full_static_path = os.path.join(settings.STATIC_ROOT, file_path)

            # ✅ Ensure the 'recordings' folder exists
            os.makedirs(os.path.dirname(full_static_path), exist_ok=True)

            # ✅ Decode and save as MP3
            with open(full_static_path, 'wb') as audio_file:
                audio_file.write(base64.b64decode(audio_base64))

            try:
                print("SCORING AUDIO")
                converted_path = full_static_path.replace('recording_','converted_')
                subprocess.run([
                    "ffmpeg", "-i", full_static_path,
                    "-ar", "48000",       # Higher sample rate
                    "-ac", "1",           # Mono audio for clarity
                    "-b:a", "192k",       # Higher bitrate for improved sound
                    converted_path
                ], check=True)

                with open(converted_path, "rb") as audio:
                        audio_base64 = base64.b64encode(audio.read()).decode("utf-8")

                selected_sentence = Sentence.objects.get(id=sentence_id)
                json_result = lc.generate_pronunciation_score(audio_base64, selected_sentence.text, 'male', 'adult')
                score_data = json.loads(json_result)
                score = score_data["overall_score"]
                print(score_data)

                # ✅ Extract and sort lowest scoring words
                sorted_words = sorted(score_data["words"], key=lambda x: x["word_score"])
                lowest_words = [word["word_text"] for word in sorted_words[:3]]
                print(lowest_words)

                underlined_sentence = selected_sentence.text
                for word in lowest_words:
                    underlined_sentence = underlined_sentence.replace(f' {word} ', f"<span class='clickable-word' data-word='{word}'> <u>{word}</u> </span>", 1)

                print(f"✅ Audio successfully saved at: {full_static_path}")
                return JsonResponse({
                    'success': True,
                    'score': score,
                    'underlined_sentence': underlined_sentence,
                    'audio_url': public_url
                })

                
            except Sentence.DoesNotExist:
                print("ERROR SCORING AUDIO")
                score = "Error: Sentence not found."

            print(f"✅ Audio successfully saved at: {full_static_path}")
            return JsonResponse({
                'success': True,
                'score': score
            })

        except Exception as e:
            print(f"❌ Error in save_audio view: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
            audio_path = el.generate_audio_file(word, 'EXAVITQu4vr4xnSDxMaL')

            # ✅ Return the URL for playback
            relative_path = os.path.relpath(audio_path, settings.STATIC_ROOT)
            audio_url = f"/static/{relative_path.replace(os.path.sep, '/')}"  # Correct path formatting for web
            return JsonResponse({'success': True, 'audio_url': audio_url})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

import subprocess

def debug_static(request):
    output = subprocess.check_output("find staticfiles/ -name '*.css'", shell=True).decode()
    return HttpResponse(f"<pre>{output}</pre>")