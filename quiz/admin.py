from django.contrib import admin
from .models import Species, Question, LeaderboardEntry

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name')
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'species', 'correct_answer')
    list_filter = ('species',)

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'score', 'created_at')
    list_filter = ('created_at',)
    