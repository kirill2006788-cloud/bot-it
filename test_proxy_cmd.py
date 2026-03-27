#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест прокси через командную строку
"""

import sys
import httpx

# Прокси из аргументов или используем дефолтный
if len(sys.argv) > 1:
    proxy_url = sys.argv[1]
else:
    proxy_url = "socks5://user:password@host:port"

print("="*60)
print("ТЕСТ ПРОКСИ")
print("="*60)
print(f"Прокси: {proxy_url}")

try:
    if proxy_url.startswith("socks5://"):
        try:
            import httpx_socks
            from httpx_socks import SyncProxyTransport
            print("\n[1/3] Создаю SOCKS5 транспорт...")
            transport = SyncProxyTransport.from_url(proxy_url)
            print("[OK] Транспорт создан")
            
            print("\n[2/3] Создаю httpx клиент...")
            client = httpx.Client(
                transport=transport,
                timeout=httpx.Timeout(10.0, connect=5.0)
            )
            print("[OK] Клиент создан")
            
            print("\n[3/3] Тестирую подключение...")
            response = client.get("https://httpbin.org/ip", timeout=10.0)
            print(f"[OK] Статус: {response.status_code}")
            print(f"[OK] IP через прокси: {response.text}")
            
            client.close()
            print("\n" + "="*60)
            print("[SUCCESS] ПРОКСИ РАБОТАЕТ!")
            print("="*60)
            
        except ImportError:
            print("[ERROR] httpx-socks не установлен!")
            print("Установите: pip install httpx-socks")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Ошибка: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # HTTP прокси
        print("\n[1/2] Создаю HTTP клиент...")
        client = httpx.Client(
            proxy=proxy_url,
            timeout=httpx.Timeout(10.0, connect=5.0)
        )
        print("[OK] Клиент создан")
        
        print("\n[2/2] Тестирую подключение...")
        response = client.get("https://httpbin.org/ip", timeout=10.0)
        print(f"[OK] Статус: {response.status_code}")
        print(f"[OK] IP через прокси: {response.text}")
        
        client.close()
        print("\n" + "="*60)
        print("[SUCCESS] ПРОКСИ РАБОТАЕТ!")
        print("="*60)

except Exception as e:
    print(f"\n[ERROR] ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

