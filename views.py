"""Views for quiz application."""

import random
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Species, Question, LeaderboardEntry
from .forms import SpeciesForm, QuestionForm, NameForm


def get_parrot_image():
    """Return random local parrot image or empty string."""
    images_dir = os.path.join(
        settings.BASE_DIR, 'quiz', 'static', 'quiz', 'images'
    )
    if os.path.exists(images_dir):
        images = [
            f for f in os.listdir(images_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        ]
        if images:
            return settings.STATIC_URL + 'quiz/images/' + random.choice(images)
    return ''


def index(request):
    """Home page with start quiz form."""
    image_url = get_parrot_image()
    form = NameForm()
    return render(
        request,
        'quiz/index.html',
        {'image_url': image_url, 'form': form}
    )


def start_quiz(request):
    """Initialize quiz session."""
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            player_name = form.cleaned_data['player_name']
            request.session['player_name'] = player_name
            request.session['current_score'] = 0
            all_qs = list(Question.objects.values_list('id', flat=True))
            random.shuffle(all_qs)
            request.session['remaining_questions'] = all_qs
            request.session['current_question_index'] = 0
            return redirect('quiz:question')
        messages.error(request, 'Invalid name')
        return redirect('quiz:index')
    return redirect('quiz:index')


def question_view(request):
    """Display current question and process answer."""
    player_name = request.session.get('player_name')
    remaining = request.session.get('remaining_questions', [])
    idx = request.session.get('current_question_index', 0)

    if not player_name or idx >= len(remaining):
        score = request.session.get('current_score', 0)
        if player_name and score > 0:
            LeaderboardEntry.objects.create(
                player_name=player_name, score=score
            )
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
    correct = question.correct_answer
    if correct not in all_species:
        all_species.append(correct)

    other_species = [name for name in all_species if name != correct]
    random.shuffle(other_species)
    choices = [correct] + other_species[:3]
    random.shuffle(choices)

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if selected == correct:
            request.session['current_score'] += 1
            request.session['current_question_index'] += 1
            if request.session['current_question_index'] >= len(remaining):
                player_name = request.session.get('player_name')
                score = request.session.get('current_score')
                LeaderboardEntry.objects.create(
                    player_name=player_name, score=score
                )
                request.session['final_score'] = score
                request.session['final_player'] = player_name
                request.session.pop('player_name', None)
                request.session.pop('remaining_questions', None)
                request.session.pop('current_question_index', None)
                request.session.pop('current_score', None)
                return redirect('quiz:result')
            return redirect('quiz:question')
        # Неправильный ответ
        score = request.session.get('current_score', 0)
        player_name = request.session.get('player_name')
        LeaderboardEntry.objects.create(
            player_name=player_name, score=score
        )
        request.session['final_score'] = score
        request.session['final_player'] = player_name
        request.session.pop('remaining_questions', None)
        request.session.pop('current_question_index', None)
        request.session.pop('current_score', None)
        request.session.pop('player_name', None)
        return redirect('quiz:result')

    context = {
        'question': question,
        'choices': choices,
        'score': request.session.get('current_score', 0),
    }
    return render(request, 'quiz/quiz.html', context)


def quit_quiz(request):
    """End the quiz prematurely and save current score."""
    player_name = request.session.get('player_name')
    score = request.session.get('current_score', 0)
    if player_name is not None:
        LeaderboardEntry.objects.create(
            player_name=player_name, score=score
        )
        request.session['final_score'] = score
        request.session['final_player'] = player_name
    request.session.pop('player_name', None)
    request.session.pop('remaining_questions', None)
    request.session.pop('current_question_index', None)
    request.session.pop('current_score', None)
    return redirect('quiz:result')


def result_view(request):
    """Display final result."""
    player_name = request.session.pop(
        'final_player', request.session.get('player_name', 'Anonymous')
    )
    score = request.session.pop(
        'final_score', request.session.get('current_score', 0)
    )
    request.session.pop('player_name', None)
    request.session.pop('remaining_questions', None)
    request.session.pop('current_question_index', None)
    request.session.pop('current_score', None)
    return render(
        request,
        'quiz/result.html',
        {'player_name': player_name, 'score': score}
    )


def leaderboard(request):
    """Show top 20 scores."""
    entries = LeaderboardEntry.objects.all()[:20]
    return render(request, 'quiz/leaderboard.html', {'entries': entries})


def species_list(request):
    """List all parrot species."""
    species = Species.objects.all()
    return render(request, 'quiz/species_list.html', {'species': species})


def species_detail(request, pk):
    """Show details of a single species."""
    species = get_object_or_404(Species, pk=pk)
    return render(request, 'quiz/species_detail.html', {'species': species})


def species_create(request):
    """Create a new species."""
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
    """Edit an existing species."""
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

def start_photo_quiz(request):
    """Инициализация фото-квиза."""
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            species_with_images = Species.objects.exclude(
                image_url__exact=''
            ).exclude(image_url__isnull=True)
            if species_with_images.count() == 0:
                messages.error(
                    request,
                    'Нет видов с изображениями. Добавьте изображения в базу.'
                )
                return redirect('quiz:index')
            player_name = form.cleaned_data['player_name']
            request.session['photo_player_name'] = player_name
            request.session['photo_current_score'] = 0
            all_ids = list(species_with_images.values_list('id', flat=True))
            random.shuffle(all_ids)
            request.session['photo_remaining_ids'] = all_ids
            request.session['photo_current_index'] = 0
            return redirect('quiz:photo_question')
        messages.error(request, 'Некорректное имя')
        return redirect('quiz:index')
    return redirect('quiz:index')


def photo_question_view(request):
    """Показ вопроса фото-квиза и обработка ответа."""
    player_name = request.session.get('photo_player_name')
    remaining = request.session.get('photo_remaining_ids', [])
    idx = request.session.get('photo_current_index', 0)

    # Проверка на завершение игры
    if not player_name or idx >= len(remaining):
        score = request.session.get('photo_current_score', 0)
        if player_name and score > 0:
            LeaderboardEntry.objects.create(
                player_name=player_name, score=score
            )
            request.session['photo_final_score'] = score
            request.session['photo_final_player'] = player_name
        request.session.pop('photo_player_name', None)
        request.session.pop('photo_remaining_ids', None)
        request.session.pop('photo_current_index', None)
        request.session.pop('photo_current_score', None)
        return redirect('quiz:photo_result')

    species_id = remaining[idx]
    species = get_object_or_404(Species, id=species_id)

    if not species.image_url:
        request.session['photo_current_index'] += 1
        return redirect('quiz:photo_question')

    all_species_names = list(Species.objects.values_list('name', flat=True))
    correct = species.name
    other_names = [n for n in all_species_names if n != correct]
    random.shuffle(other_names)
    choices = [correct] + other_names[:3]
    random.shuffle(choices)

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if selected == correct:
            request.session['photo_current_score'] += 1
            request.session['photo_current_index'] += 1
            if request.session['photo_current_index'] >= len(remaining):
                final_score = request.session['photo_current_score']
                LeaderboardEntry.objects.create(
                    player_name=player_name, score=final_score
                )
                request.session['photo_final_score'] = final_score
                request.session['photo_final_player'] = player_name
                request.session.pop('photo_player_name', None)
                request.session.pop('photo_remaining_ids', None)
                request.session.pop('photo_current_index', None)
                request.session.pop('photo_current_score', None)
                return redirect('quiz:photo_result')
            return redirect('quiz:photo_question')
        else:
            score = request.session.get('photo_current_score', 0)
            LeaderboardEntry.objects.create(
                player_name=player_name, score=score
            )
            request.session['photo_final_score'] = score
            request.session['photo_final_player'] = player_name
            request.session.pop('photo_player_name', None)
            request.session.pop('photo_remaining_ids', None)
            request.session.pop('photo_current_index', None)
            request.session.pop('photo_current_score', None)
            return redirect('quiz:photo_result')

    context = {
        'species': species,
        'choices': choices,
        'score': request.session.get('photo_current_score', 0),
        'total': len(remaining),
    }
    return render(request, 'quiz/photo_quiz.html', context)


def photo_quit(request):
    """Преждевременное завершение фото-квиза."""
    player_name = request.session.get('photo_player_name')
    score = request.session.get('photo_current_score', 0)
    if player_name is not None:
        LeaderboardEntry.objects.create(
            player_name=player_name, score=score
        )
        request.session['photo_final_score'] = score
        request.session['photo_final_player'] = player_name
    request.session.pop('photo_player_name', None)
    request.session.pop('photo_remaining_ids', None)
    request.session.pop('photo_current_index', None)
    request.session.pop('photo_current_score', None)
    return redirect('quiz:photo_result')


def photo_result_view(request):
    """Отображение результата фото-квиза."""
    player_name = request.session.pop(
        'photo_final_player',
        request.session.get('photo_player_name', 'Anonymous')
    )
    score = request.session.pop(
        'photo_final_score',
        request.session.get('photo_current_score', 0)
    )
    # Очистка остатков
    request.session.pop('photo_player_name', None)
    request.session.pop('photo_remaining_ids', None)
    request.session.pop('photo_current_index', None)
    request.session.pop('photo_current_score', None)
    return render(
        request,
        'quiz/photo_result.html',
        {'player_name': player_name, 'score': score}
    )
