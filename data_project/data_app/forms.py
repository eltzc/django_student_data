# data_app/forms.py
from django import forms
from .models import StudentData

class StudentDataForm(forms.ModelForm):
    # ... (ваш код StudentDataForm с save_to) ...
    SAVE_CHOICES = [
        ('db', 'Сохранить в базу данных'),
        ('file', 'Сохранить в файл'),
    ]
    save_to = forms.ChoiceField(
        choices=SAVE_CHOICES,
        widget=forms.RadioSelect,
        label='Куда сохранить данные?'
    )
    class Meta:
        model = StudentData
        fields = ['first_name', 'last_name', 'subject', 'grade', 'date_received', 'save_to']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'})
        }

# ЭТОТ КЛАСС ДОЛЖЕН БЫТЬ ЗДЕСЬ, В data_app/forms.py
class UploadFileForm(forms.Form):
    file = forms.FileField()