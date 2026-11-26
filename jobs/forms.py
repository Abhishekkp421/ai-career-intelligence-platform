from django import forms
from .models import JobDescription


class JobDescriptionForm(forms.ModelForm):

    title = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Python Developer'
        })
    )

    company = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. TCS, Wipro, Infosys'
        })
    )

    description_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Paste the complete job description here...'
        })
    )

    uploaded_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,application/pdf'
        })
    )

    class Meta:
        model = JobDescription
        fields = [
            'title',
            'company',
            'description_text',
            'uploaded_file'
        ]

    def clean_uploaded_file(self):
        uploaded_file = self.cleaned_data.get('uploaded_file')

        if not uploaded_file:
            return uploaded_file

        if not uploaded_file.name.lower().endswith('.pdf'):
            raise forms.ValidationError(
                'Only PDF files are allowed.'
            )

        if uploaded_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                'PDF file size must not exceed 5 MB.'
            )

        # Basic PDF signature validation
        header = uploaded_file.read(5)
        uploaded_file.seek(0)

        if header != b'%PDF-':
            raise forms.ValidationError(
                'The uploaded file is not a valid PDF.'
            )

        return uploaded_file

    def clean(self):
        cleaned_data = super().clean()

        description = (
            cleaned_data.get('description_text') or ''
        ).strip()

        uploaded_file = cleaned_data.get('uploaded_file')

        if bool(description) == bool(uploaded_file):
            raise forms.ValidationError(
                'Please either paste a job description or upload a PDF, not both.'
            )

        if description and len(description) < 50:
            self.add_error(
                'description_text',
                'Please provide at least 50 characters.'
            )

        return cleaned_data