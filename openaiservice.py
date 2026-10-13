"""Анализ конкурентов через модель (ProxyAPI, OpenAI-совместимый).

Два режима: анализ текста и анализ изображения (скриншот лендинга).
Модель возвращает структурированный JSON.
"""
import base64
import json
import re
from typing import Any, Dict, Optional

from openai import OpenAI

import config

# Промпты из урока, доработанные под нишу ИИ-сервисов для салонов красоты.
# Метка {MY_SITE} подставляется ниже описанием нашего сайта.

TEXT_PROMPT = """Ты — эксперт по конкурентному анализу рынка ИИ-сервисов и автоматизации для салонов красоты. Проанализируй предоставленный текст сайта конкурента и верни структурированный JSON-ответ.

Для сравнения вот наш сервис:
{MY_SITE}

Формат ответа (строго JSON):
{
  "strengths": ["сильная сторона 1", "сильная сторона 2"],
  "weaknesses": ["слабая сторона 1", "слабая сторона 2"],
  "unique_offers": ["уникальное предложение 1", "уникальное предложение 2"],
  "recommendations": ["рекомендация 1", "рекомендация 2"],
  "offer_clarity": 7,
  "automation_level": 6,
  "vs_allo_beauty": ["чем конкурент отличается от Allo Beauty 1", "2"],
  "summary": "Краткое резюме анализа"
}

Важно:
- Каждый массив должен содержать 3-5 пунктов
- offer_clarity — понятность и конкретность предложения для владельца салона, целое число от 0 до 10
- automation_level — глубина автоматизации: от простого чат-бота (0) до сквозной автоматизации записи, финансов, маркетинга и аналитики (10), целое число от 0 до 10
- vs_allo_beauty — в чём конкурент сильнее Allo Beauty и в чём слабее
- Опирайся только на предоставленный текст. Если данных мало (например, нет цен), прямо напиши об этом и ничего не выдумывай
- Пиши на русском языке
- Будь конкретен и практичен в рекомендациях"""

IMAGE_PROMPT = """Ты — эксперт по визуальному маркетингу и дизайну. Проанализируй изображение конкурента (скриншот сайта или баннер ИИ-сервиса для салонов красоты) и верни структурированный JSON.

Для сравнения вот наш сервис:
{MY_SITE}

Формат ответа (строго JSON):
{
  "description": "Детальное описание того, что изображено",
  "marketing_insights": ["инсайт 1", "инсайт 2"],
  "visual_style_score": 7,
  "visual_style_analysis": "Анализ визуального стиля конкурента",
  "offer_clarity": 7,
  "vs_allo_beauty": ["чем конкурент отличается от Allo Beauty 1", "2"],
  "recommendations": ["рекомендация 1", "рекомендация 2"]
}

Важно:
- visual_style_score — целое число от 0 до 10
- offer_clarity — понятность и конкретность предложения с первого экрана, целое число от 0 до 10
- Каждый массив должен содержать 3-5 пунктов
- Описывай только то, что реально видно на изображении. Если что-то нечитаемо, так и напиши
- Пиши на русском языке
- Оценивай: цветовую палитру, типографику, композицию, UX/UI элементы"""


def _build_prompt(template: str) -> str:
    return template.replace("{MY_SITE}", config.MY_SITE_DESCRIPTION)


def parse_json_response(content: str) -> Dict[str, Any]:
    """Достаёт JSON из ответа модели (даже если он обёрнут в ```json ... ```)."""
    if not content:
        return {}
    block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if block:
        content = block.group(1)
    obj = re.search(r"\{[\s\S]*\}", content)
    if obj:
        content = obj.group(0)
    try:
        data = json.loads(content)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


class OpenAIService:
    def __init__(self) -> None:
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not config.PROXY_API_KEY:
                raise RuntimeError("Не найден PROXY_API_KEY. Впишите ключ ProxyAPI в файл .env")
            self._client = OpenAI(
                api_key=config.PROXY_API_KEY,
                base_url=config.PROXY_API_BASE_URL,
            )
        return self._client

    def analyze_text(self, text: str, source: str = "") -> Dict[str, Any]:
        user_msg = "Название конкурента: {}\n\nТекст сайта:\n{}".format(source or "не указано", text)
        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _build_prompt(TEXT_PROMPT)},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content or ""
        data = parse_json_response(content)
        if not data:
            return {"error": "Модель вернула ответ не в формате JSON", "raw": content}
        return data

    def analyze_image(self, image_bytes: bytes, mime_type: str = "image/png", source: str = "") -> Dict[str, Any]:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = self.client.chat.completions.create(
            model=config.OPENAI_VISION_MODEL,
            messages=[
                {"role": "system", "content": _build_prompt(IMAGE_PROMPT)},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Название конкурента: {}. Проанализируй изображение.".format(source or "не указано")},
                        {"type": "image_url", "image_url": {"url": "data:{};base64,{}".format(mime_type, b64)}},
                    ],
                },
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        content = response.choices[0].message.content or ""
        data = parse_json_response(content)
        if not data:
            return {"error": "Модель вернула ответ не в формате JSON", "raw": content}
        return data


openai_service = OpenAIService()
