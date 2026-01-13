"""
TrueQuery API Client
Простой Python клиент для работы с TrueQuery API
"""

__version__ = "1.0.0"
__author__ = "Leo"
__license__ = "MIT"

import hashlib
import json
import time
import requests
import webbrowser
import tempfile
import os
from typing import Dict, Any, Optional
from functools import lru_cache
import sys

# ================ КОНСТАНТЫ И НАСТРОЙКИ ================

API_BASE_URL = "https://api-idh.mainplay-tg.ru"

# Маппинг endpoint'ов (защита от сканирования)
ENDPOINTS = {
    "search": "/api/search",
    "phone": "/api/phone", 
    "discord": "/api/discord",
    "status": "/api/status"
}

# Коды ошибок из apiidh.py
ERROR_CODES = {
    400: "MISSING_PARAMS",
    401: "UNAUTH_TOKEN", 
    403: "UNAUTH_TOKEN",
    503: "API_DISABLED"
}

ERROR_MESSAGES = {
    "API_DISABLED": "API временно отключен",
    "MAINTENANCE_MODE": "Проводятся технические работы",
    "UNAUTH_TOKEN": "Недействительный или просроченный токен",
    "MISSING_TOKEN": "Токен не указан",
    "MISSING_PARAMS": "Не указаны обязательные параметры",
    "INVALID_DATE_FORMAT": "Неверный формат даты",
    "MISSING_QUERY": "Не указан запрос для поиска"
}

# Глобальный кэш запросов
_REQUEST_CACHE = {}
_USER_AGENT = f"TrueQuery-Python-Client/{__version__}"

# ================ ОСНОВНЫЕ ФУНКЦИИ ================

def search(query: str, token: str, cache: bool = True) -> Dict[str, Any]:
    """
    Универсальный поиск через TrueQuery API.
    
    Автоматически определяет тип запроса:
    - Телефоны → телефонный поиск
    - Discord ID/username → Discord поиск  
    - Остальное → общий поиск
    
    Args:
        query: Строка для поиска (телефон, Discord, email, ФИО и т.д.)
        token: Ваш API токен
        cache: Включить кэширование (по умолчанию True)
    
    Returns:
        dict: Результаты поиска или информация об ошибке
        
    Raises:
        ValueError: Если query или token пустые
        
    Examples:
        >>> import truequery
        >>> result = truequery.search("79991234567", "your_token")
        >>> result = truequery.search("username#1234", "your_token")
    """
    if not query or not isinstance(query, str):
        raise ValueError("Параметр 'query' должен быть непустой строкой")
    
    if not token or not isinstance(token, str):
        raise ValueError("Параметр 'token' должен быть непустой строкой")
    
    # Проверяем кэш
    cache_key = _generate_cache_key(query, token)
    if cache and cache_key in _REQUEST_CACHE:
        cached = _REQUEST_CACHE[cache_key]
        if time.time() - cached["timestamp"] < 3600:  # Кэш на 1 час
            return cached["data"]
    
    # Определяем endpoint и параметры
    endpoint, params = _determine_search_type(query, token)
    
    try:
        response = _make_api_request(endpoint, params)
        
        # Кэшируем успешный результат
        if cache and "error" not in response:
            _REQUEST_CACHE[cache_key] = {
                "timestamp": time.time(),
                "data": response
            }
        
        return response
        
    except Exception as e:
        return {
            "error": "REQUEST_FAILED",
            "message": f"Ошибка при выполнении запроса: {str(e)}",
            "code": 500
        }


def is_alive() -> Dict[str, Any]:
    """
    Проверяет доступность и статус API.
    
    Returns:
        dict: Статус API с кодом и описанием
        
    Examples:
        >>> status = truequery.is_alive()
        >>> if status["code"] == 200:
        ...     print("API работает")
    """
    try:
        response = _make_api_request("status", {})
        
        # Анализируем ответ API
        if isinstance(response, dict):
            if "error" in response:
                error_key = response["error"]
                return {
                    "status": "error",
                    "code": ERROR_CODES.get(500, 500),
                    "message": ERROR_MESSAGES.get(error_key, "Ошибка API"),
                    "error": error_key
                }
            
            if response.get("status") == "online":
                return {
                    "status": "online",
                    "code": 200,
                    "message": "API работает нормально"
                }
        
        return {
            "status": "unknown",
            "code": 500,
            "message": "Неизвестный статус API"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "code": 503,
            "message": f"Не удалось подключиться к API: {str(e)}"
        }


def clear_cache() -> Dict[str, Any]:
    """
    Очищает кэш всех выполненных запросов.
    
    Returns:
        dict: Результат операции
        
    Examples:
        >>> truequery.clear_cache()
        {'success': True, 'cleared': 15, 'message': 'Кэш очищен'}
    """
    global _REQUEST_CACHE
    cleared_count = len(_REQUEST_CACHE)
    _REQUEST_CACHE = {}
    
    return {
        "success": True,
        "cleared": cleared_count,
        "message": f"Кэш очищен ({cleared_count} записей)"
    }


def get_stats(token: str) -> Dict[str, Any]:
    """
    Получает статистику использования для указанного токена.
    
    Args:
        token: API токен для анализа
        
    Returns:
        dict: Статистика использования
        
    Examples:
        >>> stats = truequery.get_stats("your_token")
        >>> print(f"Запросов в кэше: {stats['cached_requests']}")
    """
    if not token:
        return {
            "error": "MISSING_TOKEN",
            "message": ERROR_MESSAGES["MISSING_TOKEN"],
            "code": 400
        }
    
    # Анализируем кэш для этого токена
    token_prefix = token[:8] + "..." + token[-4:] if len(token) > 12 else token
    
    cached_for_token = 0
    unique_queries = set()
    
    for cache_key, data in _REQUEST_CACHE.items():
        if token in cache_key:
            cached_for_token += 1
            if "query" in data.get("data", {}):
                query_hash = hashlib.md5(
                    str(data["data"].get("query", "")).encode()
                ).hexdigest()
                unique_queries.add(query_hash)
    
    return {
        "token_masked": token_prefix,
        "cached_requests": cached_for_token,
        "unique_queries": len(unique_queries),
        "cache_size": len(_REQUEST_CACHE),
        "timestamp": time.time()
    }


def help():
    """
    Открывает документацию в браузере.
    
    Examples:
        >>> truequery.help()  # Откроет браузер с документацией
    """
    html_content = _generate_help_html()
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', 
        suffix='.html', 
        delete=False,
        encoding='utf-8'
    )
    
    try:
        temp_file.write(html_content)
        temp_file.close()
        
        # Открываем в браузере
        webbrowser.open(f'file://{os.path.abspath(temp_file.name)}')
        
        # Удаляем файл через 30 секунд
        import threading
        def cleanup():
            time.sleep(30)
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
        
        return {
            "success": True,
            "message": "Документация открыта в браузере",
            "file": temp_file.name
        }
        
    except Exception as e:
        return {
            "error": "HELP_ERROR",
            "message": f"Не удалось открыть документацию: {str(e)}",
            "code": 500
        }

# ================ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ================

def _generate_cache_key(query: str, token: str) -> str:
    """Генерирует уникальный ключ для кэша."""
    key_string = f"{query}:{token}"
    return hashlib.sha256(key_string.encode()).hexdigest()[:32]


def _determine_search_type(query: str, token: str) -> tuple:
    """Определяет тип поиска на основе запроса."""
    query_clean = str(query).strip().lower()
    
    # Discord ID (только цифры, 17-19 символов)
    if query_clean.isdigit() and 17 <= len(query_clean) <= 19:
        return "discord", {"token": token, "id": query_clean}
    
    # Discord username (формат username#1234)
    if '#' in query_clean:
        parts = query_clean.split('#')
        if len(parts) == 2 and len(parts[1]) == 4 and parts[1].isdigit():
            return "discord", {"token": token, "query": query_clean}
    
    # Телефон (начинается с +7 или 7, 10-11 цифр)
    digits = ''.join(filter(str.isdigit, query_clean))
    if len(digits) in [10, 11] and (digits.startswith('7') or digits.startswith('8')):
        return "phone", {"token": token, "phone": digits}
    
    # Всё остальное - общий поиск
    return "search", {"token": token, "query": query}


def _make_api_request(endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Выполняет HTTP запрос к API."""
    url = API_BASE_URL + ENDPOINTS[endpoint]
    
    headers = {
        "User-Agent": _USER_AGENT,
        "Accept": "application/json",
        "Connection": "close"
    }
    
    try:
        # Используем сессию с настройками
        session = requests.Session()
        session.headers.update(headers)
        
        # Настройка повторных попыток
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        response = session.get(
            url,
            params=params,
            timeout=300,  # 5 минут для долгих запросов
            verify=True
        )
        
        # Парсим JSON
        try:
            data = response.json()
        except ValueError:
            return {
                "error": "INVALID_RESPONSE",
                "message": "Сервер вернул некорректный ответ",
                "code": 500
            }
        
        # Обрабатываем HTTP ошибки
        if response.status_code != 200:
            error_key = ERROR_CODES.get(response.status_code, "UNKNOWN_ERROR")
            return {
                "error": error_key,
                "message": ERROR_MESSAGES.get(error_key, "Неизвестная ошибка"),
                "code": response.status_code
            }
        
        # Если API вернул ошибку в JSON
        if isinstance(data, dict) and "error" in data:
            error_key = data["error"]
            return {
                "error": error_key,
                "message": ERROR_MESSAGES.get(error_key, data.get("message", "Ошибка API")),
                "code": data.get("code", 400)
            }
        
        return data
        
    except requests.exceptions.Timeout:
        return {
            "error": "TIMEOUT",
            "message": "Превышено время ожидания ответа от сервера",
            "code": 408
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "CONNECTION_ERROR",
            "message": "Не удалось подключиться к серверу",
            "code": 503
        }
    
    except Exception as e:
        return {
            "error": "REQUEST_FAILED",
            "message": f"Ошибка при выполнении запроса: {str(e)}",
            "code": 500
        }


def _generate_help_html() -> str:
    """Генерирует HTML документацию."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>TrueQuery API Documentation v{__version__}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .code {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; margin: 15px 0; }}
        .function {{ background: #ecf0f1; padding: 15px; margin: 15px 0; border-left: 4px solid #3498db; }}
        .error {{ color: #e74c3c; background: #fadbd8; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .success {{ color: #27ae60; background: #d5f4e6; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 TrueQuery API Client v{__version__}</h1>
        
        <div class="function">
            <h2>🔍 search(query, token, cache=True)</h2>
            <p>Универсальный поиск. Автоматически определяет тип запроса.</p>
            <div class="code">
# Примеры использования:<br>
result = truequery.search("79991234567", "ваш_токен")<br>
result = truequery.search("username#1234", "ваш_токен")<br>
result = truequery.search("email@example.com", "ваш_токен")
            </div>
        </div>
        
        <div class="function">
            <h2>📊 is_alive()</h2>
            <p>Проверяет статус API. Возвращает код и сообщение.</p>
            <div class="code">
status = truequery.is_alive()<br>
if status["code"] == 200:<br>
    print("✅ API работает")<br>
else:<br>
    print(f"❌ Ошибка: {{status['message']}}")
            </div>
        </div>
        
        <div class="function">
            <h2>🧹 clear_cache()</h2>
            <p>Очищает кэш запросов в памяти.</p>
            <div class="code">
result = truequery.clear_cache()<br>
print(f"Очищено записей: {{result['cleared']}}")
            </div>
        </div>
        
        <div class="function">
            <h2>📈 get_stats(token)</h2>
            <p>Статистика использования для токена.</p>
            <div class="code">
stats = truequery.get_stats("ваш_токен")<br>
print(f"Запросов в кэше: {{stats['cached_requests']}}")
            </div>
        </div>
        
        <h2>🚨 Коды ошибок</h2>
        <div class="error">
            <strong>400</strong> - Не указаны обязательные параметры<br>
            <strong>401/403</strong> - Недействительный токен<br>
            <strong>408</strong> - Таймаут запроса<br>
            <strong>500</strong> - Внутренняя ошибка сервера<br>
            <strong>503</strong> - API временно недоступен
        </div>
        
        <h2>📦 Установка</h2>
        <div class="code">
pip install truequery-api
        </div>
        
        <div class="success">
            <strong>✅ Готово к использованию!</strong><br>
            Библиотека содержит все необходимые функции для работы с TrueQuery API.
        </div>
    </div>
</body>
</html>"""


# ================ CLI ИНТЕРФЕЙС ================

def _cli_main():
    """Точка входа для командной строки."""
    if len(sys.argv) < 2:
        print("Использование: truequery <команда>")
        print("Команды: help, status, version, clear-cache")
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        result = help()
        print(result.get("message", "Документация открыта"))
    
    elif command == "status":
        result = is_alive()
        print(f"Статус: {result.get('status', 'unknown')}")
        print(f"Код: {result.get('code')}")
        print(f"Сообщение: {result.get('message')}")
    
    elif command == "version":
        print(f"TrueQuery API Client v{__version__}")
        print(f"Автор: {__author__}")
        print(f"Лицензия: {__license__}")
    
    elif command == "clear-cache":
        result = clear_cache()
        print(f"✅ {result.get('message')}")
    
    else:
        print(f"Неизвестная команда: {command}")
        print("Доступные команды: help, status, version, clear-cache")


# ================ ЭКСПОРТ ФУНКЦИЙ ================

__all__ = [
    "search",
    "is_alive", 
    "clear_cache",
    "get_stats",
    "help",
    "__version__",
    "__author__",
    "__license__"
]

# Точка входа для CLI
if __name__ == "__main__":
    _cli_main()