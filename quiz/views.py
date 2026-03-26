import random
import os
import json
import urllib.request
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Species, Question, LeaderboardEntry
from .forms import SpeciesForm, QuestionForm, NameForm

def get_parrot_image():
   
    images_dir = os.path.join(settings.BASE_DIR, 'quiz', 'static', 'quiz', 'images')
    if os.path.exists(images_dir):
        images = [f for f in os.listdir(images_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        if images:
            return settings.STATIC_URL + 'quiz/images/' + random.choice(images)
    
def index(request):
    image_url = get_parrot_image()
    form = NameForm()
    return render(request, 'quiz/index.html', {'image_url': image_url, 'form': form})

def start_quiz(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            player_name = form.cleaned_data['player_name']
            request.session['player_name'] = player_name
            request.session['current_score'] = 0
            # Get all question ids in random order
            all_qs = list(Question.objects.values_list('id', flat=True))
            random.shuffle(all_qs)
            request.session['remaining_questions'] = all_qs
            request.session['current_question_index'] = 0
            return redirect('quiz:question')
        else:
            messages.error(request, 'Invalid name')
            return redirect('quiz:index')
    return redirect('quiz:index')

def question_view(request):
    player_name = request.session.get('player_name')
    remaining = request.session.get('remaining_questions', [])
    idx = request.session.get('current_question_index', 0)

    if not player_name or idx >= len(remaining):
        score = request.session.get('current_score', 0)
        if player_name and score > 0:
            LeaderboardEntry.objects.create(player_name=player_name, score=score)
            request.session['final_score'] = score
            request.session['final_player'] = player_name
        request.session.pop('player_name', None)
        request.session.pop('remaining_questions', None)
        request.session.pop('current_question_index', None)
        request.session.pop('current_score', None)
        return redirect('quiz:result')

    qid = remaining[idx]
    question = get_object_or_404(Question, id=qid)

    all_species = list(Species.objects.values_list('name', flat=True))
    if question.correct_answer not in all_species:
        all_species.append(question.correct_answer)
    random.shuffle(all_species)

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if selected == question.correct_answer:
            request.session['current_score'] += 1
            request.session['current_question_index'] += 1
            if request.session['current_question_index'] >= len(remaining):
                player_name = request.session.get('player_name')
                score = request.session.get('current_score')
                LeaderboardEntry.objects.create(player_name=player_name, score=score)
                request.session['final_score'] = score
                request.session['final_player'] = player_name
                request.session.pop('player_name', None)
                request.session.pop('remaining_questions', None)
                request.session.pop('current_question_index', None)
                request.session.pop('current_score', None)
                return redirect('quiz:result')
            return redirect('quiz:question')
        else:
            score = request.session.get('current_score', 0)
            player_name = request.session.get('player_name')
            LeaderboardEntry.objects.create(player_name=player_name, score=score)
            request.session['final_score'] = score
            request.session['final_player'] = player_name
            request.session.pop('remaining_questions', None)
            request.session.pop('current_question_index', None)
            request.session.pop('current_score', None)
            request.session.pop('player_name', None)
            return redirect('quiz:result')
    else:
        context = {
            'question': question,
            'choices': all_species,
            'score': request.session.get('current_score', 0),
        }
        return render(request, 'quiz/quiz.html', context)
def quit_quiz(request):
    player_name = request.session.get('player_name')
    score = request.session.get('current_score', 0)
    if player_name is not None:
        LeaderboardEntry.objects.create(player_name=player_name, score=score)
        request.session['final_score'] = score
        request.session['final_player'] = player_name
    request.session.pop('player_name', None)
    request.session.pop('remaining_questions', None)
    request.session.pop('current_question_index', None)
    request.session.pop('current_score', None)
    return redirect('quiz:result')

def result_view(request):
    player_name = request.session.pop('final_player', request.session.get('player_name', 'Anonymous'))
    score = request.session.pop('final_score', request.session.get('current_score', 0))
    request.session.pop('player_name', None)
    request.session.pop('remaining_questions', None)
    request.session.pop('current_question_index', None)
    request.session.pop('current_score', None)
    return render(request, 'quiz/result.html', {'player_name': player_name, 'score': score})

def leaderboard(request):
    entries = LeaderboardEntry.objects.all()[:20]  
    return render(request, 'quiz/leaderboard.html', {'entries': entries})

def species_list(request):
    species = Species.objects.all()
    return render(request, 'quiz/species_list.html', {'species': species})

def species_detail(request, pk):
    species = get_object_or_404(Species, pk=pk)
    return render(request, 'quiz/species_detail.html', {'species': species})

def species_create(request):
    if request.method == 'POST':
        form = SpeciesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Species added.')
            return redirect('quiz:species_list')
    else:
        form = SpeciesForm()
    return render(request, 'quiz/species_form.html', {'form': form})

def species_edit(request, pk):
    species = get_object_or_404(Species, pk=pk)
    if request.method == 'POST':
        form = SpeciesForm(request.POST, instance=species)
        if form.is_valid():
            form.save()
            messages.success(request, 'Species updated.')
            return redirect('quiz:species_detail', pk=species.pk)
    else:
        form = SpeciesForm(instance=species)
    return render(request, 'quiz/species_form.html', {'form': form})

def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added.')
            return redirect('quiz:species_list')
    else:
        form = QuestionForm()
    return render(request, 'quiz/question_form.html', {'form': form})

def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated.')
            return redirect('quiz:species_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'quiz/question_form.html', {'form': form})