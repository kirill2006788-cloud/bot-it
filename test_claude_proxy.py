#!/usr/bin/env python3
"""
Тест Claude API с прокси и без
"""
import os
import sys

# Временно отключаем прокси для теста
print("="*60)
print("ТЕСТ 1: Без прокси")
print("="*60)
os.environ['CLAUDE_PROXY'] = ''

from claude_helper import ClaudeHelper

try:
    claude = ClaudeHelper()
    response = claude.ask_question("Привет! Ответь одним словом: работает?")
    print(f"\nОтвет: {response[:100]}...")
    print("\n[OK] Работает без прокси!")
except Exception as e:
    print(f"\n[FAIL] Ошибка без прокси: {e}")

print("\n" + "="*60)
print("ТЕСТ 2: С прокси")
print("="*60)

# Включаем прокси
os.environ['CLAUDE_PROXY'] = 'http://3r65JE5:635lrtC@104.166.124.19:59234'

# Пересоздаем клиент
try:
    claude = ClaudeHelper()
    response = claude.ask_question("Привет! Ответь одним словом: работает?")
    print(f"\nОтвет: {response[:100]}...")
    print("\n[OK] Работает с прокси!")
except Exception as e:
    print(f"\n[FAIL] Ошибка с прокси: {e}")
    print("\nВозможные решения:")
    print("1. Проверьте, что прокси доступен")
    print("2. Попробуйте другой прокси")
    print("3. Проверьте API ключ в Anthropic")

