from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage  # Для сохранения файлов
from .forms import StudentDataForm, UploadFileForm
from .models import StudentData
from .utils import read_json_file, read_xml_file
import xml.etree.ElementTree as ET
import os  # Для работы с путями

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

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            # Проверка расширения файла
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension not in ['.json', '.xml']:
                return render(request, 'data_app/upload_form.html', {
                    'form': form,
                    'error_message': 'Недопустимый формат файла. Допустимы только JSON и XML.'
                })

            # Генерируем безопасное имя файла
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)  # auto generate name

            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            # Валидация содержимого файла
            if file_extension == '.json':
                data = read_json_file(file_path)
                if data is None:
                    fs.delete(filename)
                    return render(request, 'data_app/upload_form.html', {
                        'form': form,
                        'error_message': 'JSON файл не валиден.'
                    })
            else:  # .xml
                data = read_xml_file(file_path)
                if data is None:
                    fs.delete(filename)
                    return render(request, 'data_app/upload_form.html', {
                        'form': form,
                        'error_message': 'XML файл не валиден.'
                    })

            #  Сохраняем путь к файлу в сессии для отображения
            request.session['uploaded_file_path'] = file_path

            return redirect('display_file')
    else:
        form = UploadFileForm()
    return render(request, 'data_app/upload_form.html', {'form': form})

def display_file(request):
    file_path = request.session.get('uploaded_file_path')
    if not file_path:
        return render(request, 'data_app/display_file.html', {'error_message': 'Файл не был загружен.'})

    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.json':
        data = read_json_file(file_path)
    else:
        data = read_xml_file(file_path)

    if data is None:
        return render(request, 'data_app/display_file.html', {'error_message': 'Ошибка при чтении файла.'})
    
    #  Преобразуем XML-дерево в строку
    if file_extension == '.xml':
        data = ET.tostring(data, encoding='unicode')

    return render(request, 'data_app/display_file.html', {'data': data, 'file_extension': file_extension})