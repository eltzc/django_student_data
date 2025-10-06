from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import StudentDataForm, UploadFileForm
from .forms_update import StudentDataUpdateForm 
from .models import StudentData
from .utils import read_json_file, read_xml_file, export_to_json, export_to_xml
from django.http import HttpResponse
from django.http import JsonResponse
import xml.etree.ElementTree as ET
import os
import json  # Для работы с JSON


from django.shortcuts import render, redirect
from .forms import StudentDataForm, UploadFileForm
from .forms_update import StudentDataUpdateForm 
from .models import StudentData
from django.conf import settings  # Импортируем settings
from django.contrib import messages # Импортируем messages
import os
import json

def student_data_create(request):
    if request.method == 'POST':
        form = StudentDataForm(request.POST)
        if form.is_valid():
            save_to = form.cleaned_data['save_to']

            if save_to == 'db':
                # Сохранение в базу данных
                existing_student = StudentData.objects.filter(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    subject=form.cleaned_data['subject'],
                    grade=form.cleaned_data['grade'],
                    date_received=form.cleaned_data['date_received']
                ).first()

                if existing_student:
                    messages.error(request, 'Такая запись уже существует в базе данных.')
                    return render(request, 'data_app/student_data_form.html', {'form': form})
                else:
                    # Вот эти две строки должны быть:
                    student = form.save(commit=False)
                    student.save_to = 'db'  # Устанавливаем save_to
                    student.save()
                    return redirect('student_data_list')

            elif save_to == 'file':
                # Сохранение в файл (JSON)
                student_data = {
                    'firstName': form.cleaned_data['first_name'],
                    'lastName': form.cleaned_data['last_name'],
                    'subject': form.cleaned_data['subject'],
                    'grade': str(form.cleaned_data['grade']),  # Преобразуем Decimal в строку
                    'date': str(form.cleaned_data['date_received'])  # Преобразуем Date в строку
                }

                file_path = os.path.join(settings.MEDIA_ROOT, 'student_data.json')

                # Читаем существующие данные из файла (если он есть)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            existing_data = json.load(f)
                        except json.JSONDecodeError:
                            existing_data = []  # Если файл пустой или невалидный JSON
                else:
                    existing_data = []

                # Добавляем новые данные
                existing_data.append(student_data)

                # Записываем обратно в файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=4)  # Для красивого форматирования
                messages.success(request, 'Данные сохранены в файл')
                return redirect('student_data_list')
        else:
            return render(request, 'data_app/student_data_form.html', {'form': form})
    else:
        form = StudentDataForm()
    return render(request, 'data_app/student_data_form.html', {'form': form})
    
import json  # Добавляем импорт json
from django.conf import settings
from django.shortcuts import render
import os


def student_data_list(request):
    data_source = request.GET.get('data_source', 'db') # Получаем из GET-параметров, по умолчанию 'db'

    if data_source == 'db':
        # Получаем данные из базы данных
        students = StudentData.objects.all()
        if not students:  # Проверяем, есть ли данные в базе
            no_data_message = 'Нет данных о студентах в базе данных.'
        else:
            no_data_message = None
    elif data_source == 'file':
        # Получаем данные из файла (JSON)
        file_path = os.path.join(settings.MEDIA_ROOT, 'student_data.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                students = json.load(f)
            no_data_message = None  # Сбрасываем сообщение об отсутствии данных, если файл прочитан
        except FileNotFoundError:
            students = []
            no_data_message = 'Файл с данными не найден.'
        except json.JSONDecodeError:
            students = []
            no_data_message = 'Ошибка при чтении файла с данными.'
        except Exception as e:
            students = []
            no_data_message = f'Ошибка {e}'
    else:
        # Обработка некорректного значения data_source
        students = []
        no_data_message = 'Некорректно указан источник данных.'

    return render(request, 'data_app/student_data_list.html', {'students': students, 'data_source': data_source, 'no_data_message': no_data_message})

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

def display_all_files(request):
    """Отображает содержимое всех JSON/XML файлов из MEDIA_ROOT."""
    files_path = settings.MEDIA_ROOT
    files_data = []  # Список для хранения информации о файлах (имя и содержимое)

    try:
        all_files = os.listdir(files_path)
        json_xml_files = [f for f in all_files if f.endswith('.json') or f.endswith('.xml')]

        if not json_xml_files:
            return render(request, 'data_app/display_all_files.html', {'message': 'Файлы JSON/XML не найдены.'})

        for file_name in json_xml_files:
            file_path = os.path.join(files_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_extension = os.path.splitext(file_name)[1].lower()
                    if file_extension == '.json':
                        try:
                            data = json.load(f)
                            content = json.dumps(data, indent=4, ensure_ascii=False)  # Форматируем JSON
                        except json.JSONDecodeError as e:
                            content = f"Ошибка JSON: {e}"
                    elif file_extension == '.xml':
                        try:
                            tree = ET.parse(f)
                            root = tree.getroot()
                            content = ET.tostring(root, encoding='utf-8').decode('utf-8')
                        except ET.ParseError as e:
                            content = f"Ошибка XML: {e}"
                    else:
                        content = "Неизвестный формат"
                    files_data.append({'name': file_name, 'content': content}) # Добавляем данные файла в список
            except Exception as e:
                files_data.append({'name': file_name, 'content': f"Ошибка открытия: {e}"})

    except FileNotFoundError:
        return render(request, 'data_app/display_all_files.html', {'message': 'Директория не найдена.'})

    return render(request, 'data_app/display_all_files.html', {'files_data': files_data}) # Передаем список файлов в шаблон    

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

def ajax_search_students(request):
    # data_source = request.GET.get('data_source', 'db')  # Получаем источник из GET
    # if data_source != 'db': # Больше не нужно проверять settings
    #     # Если мы не в режиме работы с БД, поиск неактуален
    #     return JsonResponse({"error": "Поиск доступен только для режима базы данных."}, status=403)

    query = request.GET.get('q', '')
    
    if not query:
        # Если запрос пустой, возвращаем пустой список
        return JsonResponse({'results': []})

    # Фильтрация по полям, содержащим поисковый запрос (case-insensitive)
    results = StudentData.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(subject__icontains=query)
    ).values('id', 'first_name', 'last_name', 'subject', 'grade', 'date_received')

    # Преобразование QuerySet в список словарей
    student_list = list(results)
    
    # Django сам преобразует стандартные типы данных (str, int, Decimal) в JSON
    return JsonResponse({'results': student_list})

    
def student_data_update(request, id):
    student = get_object_or_404(StudentData, pk=id)
    if request.method == "POST":
        form = StudentDataUpdateForm(request.POST, instance=student)  # Используем новую форму
        if form.is_valid():
            form.save()
            return redirect('student_data_list')
        else:
            # Форма не прошла валидацию, ошибки будут отображены
            return render(request, 'data_app/student_data_update.html', {'form': form, 'student': student})
    else:
        form = StudentDataUpdateForm(instance=student)  # Используем новую форму
    return render(request, 'data_app/student_data_update.html', {'form': form, 'student': student})

def student_data_delete(request, id):
        
    if request.method != "POST":
        return JsonResponse({"error": "Метод не разрешен."}, status=405)

    try:
        student = StudentData.objects.get(pk=id)
        student.delete()
        return JsonResponse({"success": True, "id_deleted": id})
    except StudentData.DoesNotExist:
        return JsonResponse({"error": "Запись не найдена."}, status=404)