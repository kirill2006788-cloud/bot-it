#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подключения к Claude API
"""

import os
from dotenv import load_dotenv

load_dotenv()

from config import CLAUDE_API_KEY, CLAUDE_PROXY
from claude_helper import ClaudeHelper

print("="*60)
print("ТЕСТ ПОДКЛЮЧЕНИЯ К CLAUDE API")
print("="*60)

print(f"\nAPI Key: {CLAUDE_API_KEY[:20]}...")
print(f"Proxy: {CLAUDE_PROXY if CLAUDE_PROXY else 'НЕ НАСТРОЕН'}")

print("\n" + "="*60)
print("Создаю ClaudeHelper...")
print("="*60)

try:
    claude = ClaudeHelper()
    print("✅ ClaudeHelper создан успешно")
    
    if claude.use_proxy:
        print(f"✅ Прокси используется: {CLAUDE_PROXY.split('@')[1] if '@' in CLAUDE_PROXY else 'скрыт'}")
    else:
        print("⚠️ Прокси НЕ используется")
    
    print("\n" + "="*60)
    print("Тестирую запрос к Claude API...")
    print("="*60)
    
    response = claude.ask_question("Привет! Ответь одним словом: работает?")
    
    print(f"\n✅ УСПЕХ! Ответ: {response[:100]}")
    print("\n" + "="*60)
    print("✅ ВСЕ РАБОТАЕТ!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    print("❌ ПРОБЛЕМА С ПОДКЛЮЧЕНИЕМ")
    print("="*60)
    print("\nВозможные решения:")
    print("1. Проверьте доступность прокси")
    print("2. Проверьте интернет-соединение")
    print("3. Временно отключите прокси в config.py:")
    print("   CLAUDE_PROXY = \"\"")

