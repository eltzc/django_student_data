from django.shortcuts import render, redirect
from .forms import StudentDataForm

def student_data_create(request):
    if request.method == 'POST':
        form = StudentDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_data_list')  # После сохранения перенаправляем на список
    else:
        form = StudentDataForm()
    return render(request, 'data_app/student_data_form.html', {'form': form})

def student_data_list(request):
    # Позже добавим логику для отображения списка
    return render(request, 'data_app/student_data_list.html', {})