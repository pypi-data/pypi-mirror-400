import sys
import os

# Добавляем папку sevdy в path для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import clean_file, clean_directory

def main():
    """Главная функция Sevdy"""
    
    # Если нет аргументов или help
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "test":
        show_welcome()
        print("\n[OK] Sevdy работает! Готов к очистке кода!")
        print("[INFO] Инструмент для чистки Python кода активирован!")
        
    elif command == "clean":
        if len(sys.argv) > 2:
            path = sys.argv[2]
        else:
            print("[ERROR] Укажите файл для очистки!")
            print("[INFO] Пример: sevdy clean файл.py")
            return
        
        show_welcome()
        
        if os.path.isfile(path):
            if path.endswith('.py'):
                print(f"[FILE] Обрабатываю файл: {path}")
                clean_file(path)
            else:
                print(f"[ERROR] Файл {path} не является Python файлом!")
        else:
            print(f"[ERROR] Файл {path} не найден!")
    
    elif command == "version":
        try:
            from __init__ import __version__
            print("[INFO] Sevdy v1.0.0")
        except ImportError:
            print("[INFO] Sevdy v1.0.0")
    
    else:
        print(f"[ERROR] Неизвестная команда: {command}")
        show_help()


def show_welcome():
    """Показывает приветствие"""
    print("=" * 30)
    print("       SEVDY v1.0.0")
    print("   Your Python Code Cleaner")
    print("=" * 30)


def show_help():
    """Показывает справку"""
    show_welcome()
    print("\n[HELP] КОМАНДЫ:")
    print("  sevdy test          - Проверить работу")
    print("  sevdy clean файл.py - Очистить Python файл")
    print("  sevdy version       - Показать версию")
    print("  sevdy help          - Эта справка")
    print("\n[INFO] Примеры:")
    print("  sevdy clean my_script.py   # Очистить один файл")
    print("  sevdy test                 # Проверить работу")
    print("\n[CLEAN] Sevdy удаляет:")
    print("  • Пробелы в конце строк")
    print("  • Пустые строки в конце файла")
    print("\n[SUCCESS] Sevdy делает ваш код чище!")


if __name__ == "__main__":
    main()