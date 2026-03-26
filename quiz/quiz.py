from django import forms
from .models import Species, Question

class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = ['name', 'scientific_name', 'description', 'image_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise forms.ValidationError('Название должно содержать не менее 2 символов.')
        return name

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['species', 'text', 'correct_answer']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        species = cleaned_data.get('species')
        correct = cleaned_data.get('correct_answer')
        if species and correct and species.name != correct:
            raise forms.ValidationError('Правильный ответ должен соответствовать названию выбранного вида.')
        return cleaned_data

class NameForm(forms.Form):
    player_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Надо ввести имя, чтобы начать.'}
    )