from django import forms
from .models import Upload


class UploadsForm(forms.ModelForm):

    class Meta:
        model = Upload
        fields = ("description", "image")
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Short description of file'}),
        }
