# data_app/utils.py

import json
import xml.etree.ElementTree as ET
from defusedxml.ElementTree import parse as safe_parse  # Защита от XML-атак

def read_json_file(file_path):
    """Безопасное чтение данных из JSON-файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Ошибка при чтении JSON: {e}")  # Замените на логирование
        return None

def read_xml_file(file_path):
    """Безопасное чтение данных из XML-файла."""
    try:
        tree = safe_parse(file_path)  # Используем defusedxml
        root = tree.getroot()
        return root
    except Exception as e:
        print(f"Ошибка при чтении XML: {e}")  # Замените на логирование
        return None

def export_to_json(students, file_path):
    """Экспорт данных о студентах в JSON-файл."""
    data = []
    for student in students:
        data.append({
            'firstName': student.first_name,
            'lastName': student.last_name,
            'subject': student.subject,
            'grade': str(student.grade),  # Преобразуем Decimal в строку
            'date': str(student.date_received)  # Преобразуем Date в строку
        })
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при экспорте в JSON: {e}")  # Замените на логирование
        return False
    return True

def export_to_xml(students, file_path):
    """Экспорт данных о студентах в XML-файл."""
    root = ET.Element('students')
    for student in students:
        student_element = ET.SubElement(root, 'student')
        ET.SubElement(student_element, 'firstName').text = student.first_name
        ET.SubElement(student_element, 'lastName').text = student.last_name
        ET.SubElement(student_element, 'subject').text = student.subject
        ET.SubElement(student_element, 'grade').text = str(student.grade)  # Преобразуем Decimal в строку
        ET.SubElement(student_element, 'date').text = str(student.date_received)  # Преобразуем Date в строку
    try:
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"Ошибка при экспорте в XML: {e}")  # Замените на логирование
        return False
    return True