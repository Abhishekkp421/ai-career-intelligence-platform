from django import forms
from .models import CandidateProfile


class CandidateProfileForm(forms.ModelForm):

    technical_skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Python, Django, SQL, Machine Learning'
        }),
        help_text='Enter skills separated by commas.'
    )

    soft_skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Communication, Teamwork, Problem Solving'
        }),
        help_text='Enter skills separated by commas.'
    )

    class Meta:
        model = CandidateProfile
        fields = [
            'full_name',
            'phone',
            'education',
            'specialization',
            'graduation_year',
            'technical_skills',
            'soft_skills',
            'target_role',
            'career_interests',
            'preferred_location',
            'experience_level',
            'career_goal',
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'education': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'B.Tech'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Computer Science and Engineering (AIML)'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2027'
            }),
            'target_role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python Developer'
            }),
            'career_interests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your professional interests'
            }),
            'preferred_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Remote, Noida, Bengaluru...'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'career_goal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your short-term and long-term career goals'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.initial['technical_skills'] = ', '.join(
                self.instance.technical_skills or []
            )
            self.initial['soft_skills'] = ', '.join(
                self.instance.soft_skills or []
            )

    def clean_graduation_year(self):
        year = self.cleaned_data.get('graduation_year')

        if year and not 1950 <= year <= 2100:
            raise forms.ValidationError(
                'Enter a valid graduation year.'
            )

        return year

    def save(self, commit=True):
        profile = super().save(commit=False)

        profile.technical_skills = [
            skill.strip()
            for skill in self.cleaned_data.get(
                'technical_skills', ''
            ).split(',')
            if skill.strip()
        ]

        profile.soft_skills = [
            skill.strip()
            for skill in self.cleaned_data.get(
                'soft_skills', ''
            ).split(',')
            if skill.strip()
        ]

        if commit:
            profile.save()

        return profile