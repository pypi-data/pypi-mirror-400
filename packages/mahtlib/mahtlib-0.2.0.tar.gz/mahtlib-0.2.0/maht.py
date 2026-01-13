"""
MAHT - Минимальная библиотека для OpenAI API
Использование: maht("Ваш вопрос")
"""

import urllib.request
import json

_API_KEY = "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"


def maht(text: str) -> str:
    """
    Отправляет текст в ChatGPT и возвращает ответ.
    
    Пример:
        >>> from maht import maht
        >>> maht("Привет! Что такое ИИ?")
    """
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": text}]
    }
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_API_KEY}"
        }
    )
    
    with urllib.request.urlopen(req) as res:
        result = json.loads(res.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
