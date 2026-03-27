"""Database models for quiz application."""

from django.db import models
from django.core.exceptions import ValidationError


class Species(models.Model):
    """Species of parrot."""

    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    image_url = models.URLField(blank=True)

    def clean(self):
        """Validate species name."""
        if len(self.name) < 2:
            raise ValidationError({'name': 'Название должно содержать не менее 2 символов.'})
        if self.name and self.name.strip() == '':
            raise ValidationError({'name': 'Название не может быть пустым.'})

    def save(self, *args, **kwargs):
        """Save with full clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation."""
        return str(self.name)


class Question(models.Model):
    """Question for quiz."""

    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    correct_answer = models.CharField(max_length=100)

    class Meta:
        """Meta options for Question."""

        unique_together = ('species', 'text')

    def __str__(self):
        """String representation."""
        return str(self.text)


class LeaderboardEntry(models.Model):
    """Entry in leaderboard."""

    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for LeaderboardEntry."""

        ordering = ['-score', 'created_at']