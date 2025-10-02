from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage  # Для сохранения файлов
from .forms import StudentDataForm, UploadFileForm
from .models import StudentData
from .utils import read_json_file, read_xml_file
from django.http import HttpResponse
from .utils import export_to_json, export_to_xml
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
    students = StudentData.objects.all()
    if not students:  # Проверяем, есть ли данные в базе
        return render(request, 'data_app/student_data_list.html', {'students': students, 'no_data_message': 'Нет данных о студентах.'})

    return render(request, 'data_app/student_data_list.html', {'students': students})

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
            filename = fs.save(uploaded_file.name, uploaded_file)

            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            if file_extension == '.json':
                data = read_json_file(file_path)
                if data is None:
                    fs.delete(filename)
                    return render(request, 'data_app/upload_form.html', {
                        'form': form,
                        'error_message': 'JSON файл не валиден.'
                    })
                # Сохраняем JSON данные в базу
                for item in data:
                    try:
                        StudentData.objects.create(
                            first_name=item.get('firstName', ''),
                            last_name=item.get('lastName', ''),
                            subject=item.get('subject', ''),
                            grade=item.get('grade', ''),
                            date_received=item.get('date', '')
                        )
                    except Exception as e:
                        print(f"Ошибка при сохранении JSON: {e}")  # Замените на логирование
                        return render(request, 'data_app/upload_form.html', {
                            'form': form,
                            'error_message': f'Ошибка при сохранении данных из JSON: {e}'
                        })
            else:  # .xml
                root = read_xml_file(file_path)
                if root is None:
                    fs.delete(filename)
                    return render(request, 'data_app/upload_form.html', {
                        'form': form,
                        'error_message': 'XML файл не валиден.'
                    })
                # Сохраняем XML данные в базу
                for student_element in root.findall('student'):
                    try:
                        StudentData.objects.create(
                            first_name=student_element.find('firstName').text,
                            last_name=student_element.find('lastName').text,
                            subject=student_element.find('subject').text,
                            grade=student_element.find('grade').text,
                            date_received=student_element.find('date').text
                        )
                    except Exception as e:
                        print(f"Ошибка при сохранении XML: {e}")  # Замените на логирование
                        return render(request, 'data_app/upload_form.html', {
                            'form': form,
                            'error_message': f'Ошибка при сохранении данных из XML: {e}'
                        })

            # Удаляем файл после сохранения
            fs.delete(filename)

            return redirect('student_data_list')  # Перенаправляем на список

    else:
        form = UploadFileForm()
    return render(request, 'data_app/upload_form.html', {'form': form})

def display_file(request):
    file_path = request.session.get('uploaded_file_path')
    if not file_path:
        return render(request, 'data_app/display_file.html', {'error_message': 'Файл не был загружен.'})

    file_extension = os.path.splitext(file_path)[1].lower()

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        return render(request, 'data_app/display_file.html', {'error_message': 'Файл не найден.'})

    if file_extension == '.json':
        data = read_json_file(file_path)
    else:  # .xml
        data = read_xml_file(file_path)

    if data is None:
        return render(request, 'data_app/display_file.html', {'error_message': 'Ошибка при чтении файла.'})

    # Преобразуем XML-дерево в строку
    if file_extension == '.xml':
        data = ET.tostring(data, encoding='unicode')

    return render(request, 'data_app/display_file.html', {'data': data, 'file_extension': file_extension})
    
def export_data(request, format):
    """Экспорт данных о студентах в JSON или XML."""
    students = StudentData.objects.all()
    if format == 'json':
        file_path = os.path.join(settings.MEDIA_ROOT, 'students.json')
        if export_to_json(students, file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                response = HttpResponse(f.read(), content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="students.json"'
            os.remove(file_path)  # Удаляем временный файл
            return response
        else:
            return HttpResponse("Ошибка при экспорте в JSON", status=500)
    elif format == 'xml':
        file_path = os.path.join(settings.MEDIA_ROOT, 'students.xml')
        if export_to_xml(students, file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                response = HttpResponse(f.read(), content_type='application/xml')
                response['Content-Disposition'] = 'attachment; filename="students.xml"'
            os.remove(file_path)  # Удаляем временный файл
            return response
        else:
            return HttpResponse("Ошибка при экспорте в XML", status=500)
    else:
        return HttpResponse("Недопустимый формат", status=400)    