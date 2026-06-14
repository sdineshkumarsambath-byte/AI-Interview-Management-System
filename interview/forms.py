from django import forms
from .models import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'email', 'file']   # ✅ email added

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Candidate Name'
            }),
            'email': forms.EmailInput(attrs={   # ✅ NEW
                'class': 'form-control',
                'placeholder': 'Enter Email'
            }),
        }