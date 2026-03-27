"""Forms for quiz application."""

from django import forms
from .models import Species, Question


class SpeciesForm(forms.ModelForm):
    """Form for creating/editing a species."""

    class Meta:
        """Meta options for SpeciesForm."""

        model = Species
        fields = ['name', 'scientific_name', 'description', 'image_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_name(self):
        """Validate species name."""
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise forms.ValidationError('Название должно содержать не менее 2 символов.')
        if name and name.strip() == '':
            raise forms.ValidationError('Название не может быть пустым.')
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if Species.objects.exclude(pk=instance.pk).filter(name=name).exists():   # pylint: disable=no-member
                raise forms.ValidationError('Этот вид уже добавлен.')
        else:
            if Species.objects.filter(name=name).exists():   # pylint: disable=no-member
                raise forms.ValidationError('Этот вид уже добавлен.')
        return name


class QuestionForm(forms.ModelForm):
    """Form for creating/editing a question."""

    class Meta:
        """Meta options for QuestionForm."""

        model = Question
        fields = ['species', 'text', 'correct_answer']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        """Validate question data."""
        cleaned_data = super().clean()
        species = cleaned_data.get('species')
        correct = cleaned_data.get('correct_answer')
        if species and correct and species.name != correct:
            raise forms.ValidationError('Правильный ответ должен соответствовать названию вида.')
        text = cleaned_data.get('text')
        if species and text:
            instance = getattr(self, 'instance', None)
            qs = Question.objects.filter(species=species, text=text)   # pylint: disable=no-member
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise forms.ValidationError('Такой вопрос уже существует для данного вида.')
        return cleaned_data


class NameForm(forms.Form):
    """Form for player name input."""

    player_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Надо ввести имя, чтобы начать.'}
    )