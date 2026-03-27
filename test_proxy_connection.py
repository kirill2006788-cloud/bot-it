#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подключения через прокси
"""

import os
from dotenv import load_dotenv

load_dotenv()

from config import CLAUDE_PROXY

print("="*60)
print("ТЕСТ ПОДКЛЮЧЕНИЯ ЧЕРЕЗ ПРОКСИ")
print("="*60)

if not CLAUDE_PROXY:
    print("❌ Прокси не настроен")
    exit(1)

print(f"\nПрокси: {CLAUDE_PROXY}")

try:
    import httpx
    
    print("\n" + "="*60)
    print("Тест 1: HTTP запрос через прокси")
    print("="*60)
    
    if CLAUDE_PROXY.startswith("socks5://"):
        try:
            import httpx_socks
            from httpx_socks import SyncProxyTransport
            transport = SyncProxyTransport.from_url(CLAUDE_PROXY)
            client = httpx.Client(
                transport=transport,
                timeout=httpx.Timeout(10.0, connect=5.0)
            )
        except Exception as e:
            print(f"❌ Ошибка создания SOCKS5 транспорта: {e}")
            exit(1)
    else:
        client = httpx.Client(
            proxy=CLAUDE_PROXY,
            timeout=httpx.Timeout(10.0, connect=5.0)
        )
    
    # Тестируем подключение к простому сайту
    try:
        response = client.get("https://httpbin.org/ip", timeout=10.0)
        if response.status_code == 200:
            print(f"✅ Прокси работает! IP: {response.text}")
        else:
            print(f"⚠️ Прокси вернул статус {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения через прокси: {e}")
        print("\nВозможные причины:")
        print("1. Прокси недоступен")
        print("2. Неправильные учетные данные")
        print("3. Прокси заблокирован")
    finally:
        client.close()
    
    print("\n" + "="*60)
    print("Тест 2: Подключение к Anthropic API")
    print("="*60)
    
    if CLAUDE_PROXY.startswith("socks5://"):
        transport = SyncProxyTransport.from_url(CLAUDE_PROXY)
        client = httpx.Client(
            transport=transport,
            timeout=httpx.Timeout(30.0, connect=10.0)
        )
    else:
        client = httpx.Client(
            proxy=CLAUDE_PROXY,
            timeout=httpx.Timeout(30.0, connect=10.0)
        )
    
    try:
        # Пробуем подключиться к Anthropic API
        response = client.get("https://api.anthropic.com/v1/messages", timeout=30.0)
        print(f"Статус: {response.status_code}")
        if response.status_code == 401:
            print("✅ Подключение работает! (401 - ожидаемо, нужен API ключ)")
        else:
            print(f"Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Ошибка подключения к Anthropic API: {e}")
    finally:
        client.close()
    
except ImportError:
    print("❌ httpx не установлен. Установите: pip install httpx httpx-socks")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

