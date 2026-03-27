#!/usr/bin/env python3
"""
Тест модели Vosk - проверка установки и работы
"""
import os
import sys

def test_vosk_installation():
    """Проверить установку Vosk"""
    print("=" * 60)
    print("Тест установки Vosk")
    print("=" * 60)
    
    # Проверка импорта
    try:
        import vosk
        print("✅ Vosk установлен")
    except ImportError:
        print("❌ Vosk не установлен")
        print("Установите: pip install vosk")
        return False
    
    # Поиск модели
    print("\nПоиск модели Vosk...")
    base_dir = os.path.dirname(__file__)
    possible_dirs = [
        os.path.join(base_dir, "vosk_models"),
        os.path.join(os.getcwd(), "vosk_models"),
        "/opt/bot/vosk_models",
    ]
    
    model_found = False
    model_path = None
    
    for vosk_dir in possible_dirs:
        if os.path.exists(vosk_dir):
            print(f"📁 Найдена папка: {vosk_dir}")
            for item in os.listdir(vosk_dir):
                item_path = os.path.join(vosk_dir, item)
                if os.path.isdir(item_path):
                    # Проверяем структуру модели
                    has_am = os.path.exists(os.path.join(item_path, "am"))
                    has_graph = os.path.exists(os.path.join(item_path, "graph"))
                    
                    if has_am or has_graph:
                        model_path = item_path
                        model_found = True
                        print(f"✅ Найдена модель: {model_path}")
                        print(f"   - Папка am/: {'✅' if has_am else '❌'}")
                        print(f"   - Папка graph/: {'✅' if has_graph else '❌'}")
                        break
            if model_found:
                break
    
    if not model_found:
        print("❌ Модель не найдена")
        print("\n💡 Установите модель:")
        print("   1. Создайте папку: mkdir -p vosk_models")
        print("   2. Скачайте модель с https://alphacephei.com/vosk/models")
        print("   3. Распакуйте в папку vosk_models/")
        return False
    
    # Попытка загрузить модель
    print(f"\nЗагрузка модели из {model_path}...")
    try:
        model = vosk.Model(model_path)
        print("✅ Модель загружена успешно!")
        
        # Создаем распознаватель
        rec = vosk.KaldiRecognizer(model, 16000)
        print("✅ Распознаватель создан!")
        
        print("\n🎉 Все готово! Модель работает корректно.")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vosk_installation()
    sys.exit(0 if success else 1)

