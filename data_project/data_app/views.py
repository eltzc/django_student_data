from django.shortcuts import render, redirect
from .forms import StudentDataForm
from .models import StudentData  # <- Импортируйте модель StudentData

def student_data_create(request):
    if request.method == 'POST':
        form = StudentDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_data_list')
    else:
        form = StudentDataForm()
    return render(request, 'data_app/student_data_form.html', {'form': form})

def student_data_list(request):
    students = StudentData.objects.all()  # <- Получите все записи из базы данных
    return render(request, 'data_app/student_data_list.html', {'students': students})  # <- Передайте их в шаблон