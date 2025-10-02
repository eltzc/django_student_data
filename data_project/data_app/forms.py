from django import forms
from .models import StudentData

class StudentDataForm(forms.ModelForm):
    class Meta:
        model = StudentData
        fields = ['first_name', 'last_name', 'subject', 'grade', 'date_received']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'})
        }