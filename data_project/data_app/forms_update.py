# data_app/forms_update.py
from django import forms
from .models import StudentData

class StudentDataUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentData
        # Здесь нет save_to
        fields = ['first_name', 'last_name', 'subject', 'grade', 'date_received']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'})
        }