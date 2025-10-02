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