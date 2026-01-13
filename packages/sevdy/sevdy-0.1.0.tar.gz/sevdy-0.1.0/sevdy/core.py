#!/usr/bin/env python3
"""
Sevdy Core - основная логика очистки кода
"""

import os

def clean_file(filepath):
    """
    Очищает один файл:
    - Убирает пробелы в конце строк
    - Удаляет пустые строки в конце файла
    """
    print(f"[CLEAN] Sevdy чистит: {filepath}")
    
    # Читаем файл
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Разбиваем на строки
    lines = content.split('\n')
    original_count = len(lines)
    
    # 1. Убираем пробелы в конце каждой строки
    lines = [line.rstrip() for line in lines]
    
    # 2. Удаляем пустые строки в конце файла
    while lines and lines[-1] == '':
        lines.pop()
    
    # Собираем обратно
    new_content = '\n'.join(lines)
    new_count = len(lines)
    
    # Сохраняем результат
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Статистика
    removed = original_count - new_count
    if removed > 0:
        print(f"[SUCCESS] Удалено {removed} строк мусора!")
    else:
        print(f"[INFO] Файл уже чист!")
    
    return removed


def clean_directory(directory='.'):
    """
    Очищает все Python файлы в директории
    """
    print(f"[START] Sevdy запущен в: {os.path.abspath(directory)}")
    print("=" * 50)
    
    total_removed = 0
    files_cleaned = 0
    
    # Ищем все .py файлы
    for root, dirs, files in os.walk(directory):
        # Пропускаем системные папки
        if 'pycache' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    removed = clean_file(filepath)
                    total_removed += removed
                    files_cleaned += 1
                except Exception as e:
                    print(f"[ERROR] Ошибка в {file}: {e}")
    
    # Отчёт
    print("=" * 50)
    print(f"[RESULT] ИТОГ:")
    print(f"   [FILES] Файлов очищено: {files_cleaned}")
    print(f"   [LINES] Строк удалено: {total_removed}")
    
    if files_cleaned > 0:
        avg = total_removed / files_cleaned
        print(f"   [AVG] В среднем: {avg:.1f} строк/файл")
    
    print("\n[INFO] Sevdy: Чистый код — твой код!")
    
    return total_removed