"""URL configuration for quiz app."""

from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start_quiz, name='start'),
    path('question/', views.question_view, name='question'),
    path('result/', views.result_view, name='result'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('species/', views.species_list, name='species_list'),
    path('species/<int:pk>/', views.species_detail, name='species_detail'),
    path('species/create/', views.species_create, name='species_create'),
    path('species/<int:pk>/edit/', views.species_edit, name='species_edit'),
    path('question/create/', views.question_create, name='question_create'),
    path('question/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('quit/', views.quit_quiz, name='quit'),

    path('photo-start/', views.start_photo_quiz, name='photo_start'),
    path('photo-question/', views.photo_question_view, name='photo_question'),
    path('photo-quit/', views.photo_quit, name='photo_quit'),
]