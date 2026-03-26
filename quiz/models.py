"""from django.db import models

class Species(models.Model):
    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    correct_answer = models.CharField(max_length=100)  # species.name

    def __str__(self):
        return self.text

class LeaderboardEntry(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', 'created_at']"""
from django.db import models
from django.core.exceptions import ValidationError

class Species(models.Model):
    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    image_url = models.URLField(blank=True)

    def clean(self):
        if len(self.name) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters long.'})
        if self.name and self.name.strip() == '':
            raise ValidationError({'name': 'Name cannot be empty or whitespace.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Question(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    correct_answer = models.CharField(max_length=100)

    class Meta:
        unique_together = ('species', 'text')

    def __str__(self):
        return self.text

class LeaderboardEntry(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', 'created_at']