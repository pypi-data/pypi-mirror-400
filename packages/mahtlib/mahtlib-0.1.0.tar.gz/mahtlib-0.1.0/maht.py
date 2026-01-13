"""
MAHT - Минимальная библиотека для работы с OpenAI API
Использование: maht("Ваш вопрос")
"""

import urllib.request
import json
from typing import Optional


class MahtConfig:
    """Конфигурация для MAHT (Single Responsibility Principle)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        api_url: str = "https://api.openai.com/v1/chat/completions"
    ):
        self.api_key = api_key
        self.model = model
        self.api_url = api_url


class MahtClient:
    """Клиент для отправки запросов к OpenAI API (Open/Closed Principle)"""
    
    def __init__(self, config: MahtConfig):
        self._config = config
    
    def send(self, text: str) -> str:
        """Отправляет запрос и возвращает ответ"""
        data = {
            "model": self._config.model,
            "messages": [
                {"role": "user", "content": text}
            ]
        }
        
        req = urllib.request.Request(
            self._config.api_url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.api_key}"
            }
        )
        
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]


# Глобальный клиент для простого использования
_client: Optional[MahtClient] = None


def setup(api_key: str, model: str = "gpt-4o-mini") -> None:
    """Настройка библиотеки с API ключом"""
    global _client
    config = MahtConfig(api_key=api_key, model=model)
    _client = MahtClient(config)


def maht(text: str) -> str:
    """
    Отправляет текст в OpenAI и возвращает ответ.
    
    Пример:
        >>> from maht import maht, setup
        >>> setup("your-api-key")
        >>> maht("Привет! Что такое ИИ?")
    """
    if _client is None:
        raise RuntimeError("Сначала вызовите setup('your-api-key')")
    
    return _client.send(text)


# Для ещё более простого использования - можно импортировать напрямую
__all__ = ["maht", "setup", "MahtConfig", "MahtClient"]
