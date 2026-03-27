#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры использования AI генерации изображений
Демонстрация возможностей ImageGenerator
"""

from image_generator import ImageGenerator
from claude_helper import ClaudeHelper

def example_basic():
    """Базовый пример генерации"""
    print("=" * 60)
    print("ПРИМЕР 1: Базовая генерация изображения")
    print("=" * 60)
    
    generator = ImageGenerator()
    prompt = "кот программист за компьютером"
    
    try:
        print(f"\n📝 Промпт: {prompt}")
        print("🎨 Генерация изображения...")
        
        image, final_prompt = generator.generate_image(prompt)
        
        print(f"✅ Изображение сгенерировано!")
        print(f"🚀 Итоговый промпт: {final_prompt}")
        
        # Сохранение
        with open("generated_cat_programmer.png", "wb") as f:
            f.write(image.getvalue())
        print("💾 Сохранено как: generated_cat_programmer.png")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def example_with_claude_enhancement():
    """Пример с улучшением промпта через Claude"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Генерация с улучшением через Claude AI")
    print("=" * 60)
    
    generator = ImageGenerator()
    claude = ClaudeHelper()
    
    simple_prompt = "дракон"
    
    try:
        print(f"\n📝 Простой промпт: {simple_prompt}")
        print("🧠 Claude AI улучшает промпт...")
        
        image, enhanced_prompt = generator.generate_image(
            simple_prompt,
            enhance_with_claude=claude
        )
        
        print(f"\n✅ Изображение сгенерировано!")
        print(f"🎨 Улучшенный промпт:\n   {enhanced_prompt}")
        
        # Сохранение
        with open("generated_dragon.png", "wb") as f:
            f.write(image.getvalue())
        print("\n💾 Сохранено как: generated_dragon.png")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def example_with_style():
    """Пример добавления стиля"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Генерация с определенным стилем")
    print("=" * 60)
    
    generator = ImageGenerator()
    
    prompt = "космический корабль"
    style = "cyberpunk"
    
    try:
        # Добавляем стиль к промпту
        styled_prompt = generator.add_style_to_prompt(prompt, style)
        
        print(f"\n📝 Оригинальный промпт: {prompt}")
        print(f"🎨 Стиль: {style}")
        print(f"🚀 Итоговый промпт: {styled_prompt}")
        print("🎨 Генерация изображения...")
        
        image, final_prompt = generator.generate_image(styled_prompt)
        
        print(f"\n✅ Изображение сгенерировано!")
        
        # Сохранение
        with open("generated_spaceship_cyberpunk.png", "wb") as f:
            f.write(image.getvalue())
        print("💾 Сохранено как: generated_spaceship_cyberpunk.png")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def example_available_styles():
    """Показать доступные стили"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Доступные художественные стили")
    print("=" * 60)
    
    generator = ImageGenerator()
    styles = generator.get_available_styles()
    
    print("\n🎨 Доступные стили для генерации:")
    for i, style in enumerate(styles, 1):
        print(f"   {i}. {style}")
    
    print("\n💡 Используйте их в промптах:")
    print("   Пример: 'дом, realistic photo style, high quality, detailed'")


def example_batch_prompts():
    """Примеры различных промптов"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 5: Коллекция крутых промптов")
    print("=" * 60)
    
    cool_prompts = [
        {
            "category": "🖥️ Для разработчиков",
            "prompts": [
                "логотип IT стартапа, минималистичный, синие тона",
                "иконка приложения в стиле flat design",
                "концепт дизайна мобильного приложения"
            ]
        },
        {
            "category": "🎨 Абстракция",
            "prompts": [
                "абстрактный фон с градиентом, современный",
                "геометрические фигуры, минимализм",
                "цифровое искусство, неоновые цвета"
            ]
        },
        {
            "category": "🌍 Пейзажи",
            "prompts": [
                "горы на рассвете, туман, кинематографично",
                "футуристический город ночью, небоскребы",
                "тропический пляж, кристально чистая вода"
            ]
        },
        {
            "category": "🦄 Фантазия",
            "prompts": [
                "дракон летит над замком, fantasy art",
                "волшебный лес с светящимися грибами",
                "космический корабль, научная фантастика"
            ]
        },
        {
            "category": "🎮 Игровой стиль",
            "prompts": [
                "персонаж в стиле пиксель арт, 8-бит",
                "сцена из РПГ игры, изометрический вид",
                "игровой интерфейс, HUD элементы"
            ]
        }
    ]
    
    for category_data in cool_prompts:
        print(f"\n{category_data['category']}:")
        for i, prompt in enumerate(category_data['prompts'], 1):
            print(f"   {i}. {prompt}")
    
    print("\n💡 Копируй и используй с командой /image!")


def example_validation():
    """Пример валидации промптов"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 6: Валидация промптов")
    print("=" * 60)
    
    from image_generator import validate_prompt
    
    test_prompts = [
        ("кот программист", True),
        ("x", False),  # Слишком короткий
        ("" * 1001, False),  # Слишком длинный
        ("описание", True),
        ("", False),  # Пустой
    ]
    
    print("\n🔍 Проверка различных промптов:\n")
    for prompt, expected in test_prompts:
        display_prompt = prompt if len(prompt) < 50 else prompt[:50] + "..."
        is_valid = validate_prompt(prompt)
        status = "✅" if is_valid else "❌"
        print(f"{status} '{display_prompt}' - {'Valid' if is_valid else 'Invalid'}")


def example_api_comparison():
    """Сравнение различных API"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 7: Информация о доступных API")
    print("=" * 60)
    
    apis = {
        "Pollinations.ai": {
            "Цена": "🆓 Бесплатно",
            "Качество": "⭐⭐⭐ Хорошее",
            "Скорость": "⚡ Быстро",
            "Регистрация": "❌ Не нужна",
            "Лимиты": "✅ Нет"
        },
        "OpenAI DALL-E 3": {
            "Цена": "💰 От $0.04/изображение",
            "Качество": "⭐⭐⭐⭐⭐ Отличное",
            "Скорость": "⏳ Средне",
            "Регистрация": "✅ Нужна",
            "Лимиты": "⚠️ Rate limits"
        }
    }
    
    for api_name, features in apis.items():
        print(f"\n{api_name}:")
        for feature, value in features.items():
            print(f"   {feature}: {value}")


def main():
    """Главная функция - запуск всех примеров"""
    print("\n")
    print("=" * 60)
    print("🎨 AI IMAGE GENERATION - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 60)
    print("\nВыберите пример для запуска:")
    print("\n1. Базовая генерация")
    print("2. Генерация с улучшением через Claude")
    print("3. Генерация с определенным стилем")
    print("4. Показать доступные стили")
    print("5. Коллекция крутых промптов")
    print("6. Валидация промптов")
    print("7. Сравнение API")
    print("8. Запустить все примеры")
    print("0. Выход")
    
    examples = {
        "1": example_basic,
        "2": example_with_claude_enhancement,
        "3": example_with_style,
        "4": example_available_styles,
        "5": example_batch_prompts,
        "6": example_validation,
        "7": example_api_comparison,
    }
    
    choice = input("\nВведите номер примера: ").strip()
    
    if choice == "0":
        print("\n👋 До встречи!")
        return
    elif choice == "8":
        for func in examples.values():
            func()
    elif choice in examples:
        examples[choice]()
    else:
        print("❌ Неверный выбор!")
        return
    
    print("\n" + "=" * 60)
    print("✅ Примеры завершены!")
    print("=" * 60)
    print("\n💡 Для использования в боте:")
    print("   /image ваше описание")
    print("\n📚 Больше информации в IMAGE_GENERATION_GUIDE.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

