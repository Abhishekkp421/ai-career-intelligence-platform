
from django import forms
from .models import Resume


class ResumeUploadForm(forms.ModelForm):

    class Meta:
        model = Resume
        fields = ['file']

        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if not file:
            raise forms.ValidationError(
                "Please select a resume PDF."
            )

        # PDF extension validation
        if not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError(
                "Only PDF files are allowed."
            )

        # Maximum file size: 5 MB
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "File size must not exceed 5 MB."
            )

        # Basic PDF signature validation
        if file.read(5) != b'%PDF-':
            raise forms.ValidationError(
                "Invalid PDF file."
            )

        file.seek(0)

        return file
