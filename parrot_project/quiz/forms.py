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
            raise forms.ValidationError('Name must be at least 2 characters long.')
        if name and name.strip() == '':
            raise forms.ValidationError('Name cannot be empty or whitespace.')
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if Species.objects.exclude(pk=instance.pk).filter(name=name).exists():
                raise forms.ValidationError('A species with this name already exists.')
        else:
            if Species.objects.filter(name=name).exists():
                raise forms.ValidationError('A species with this name already exists.')
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
            raise forms.ValidationError('Correct answer must match the selected species name.')
        text = cleaned_data.get('text')
        if species and text:
            instance = getattr(self, 'instance', None)
            qs = Question.objects.filter(species=species, text=text)
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise forms.ValidationError('A question with this text already exists for this species.')
        return cleaned_data

class NameForm(forms.Form):
    player_name = forms.CharField(
        max_length=100,
        label='Your name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please enter your name to start the quiz.'}
    )