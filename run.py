"""FastAPI-приложение «Мониторинг конкурентов».

Запуск:  uvicorn run:app --reload
Документация и тест эндпоинтов в браузере:  http://127.0.0.1:8000/docs
"""
import mimetypes
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

import config
import history
import telegram_sender
from openaiservice import openai_service
from parsingservice import page_to_prompt_text, parse_page

app = FastAPI(title="Мониторинг конкурентов", description="Анализ конкурентов Allo Beauty: текст, изображения, парсинг сайтов")

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


class TextRequest(BaseModel):
    text: str
    source: Optional[str] = ""


class ParseRequest(BaseModel):
    url: str
    name: Optional[str] = ""


def _fail(e: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail="{}: {}".format(type(e).__name__, e))


def _maybe_send(results: List[Dict[str, Any]], send_to_telegram: bool) -> Optional[str]:
    if not send_to_telegram:
        return None
    try:
        telegram_sender.send_message(telegram_sender.format_report(results))
        return "отправлено в Telegram"
    except Exception as e:
        return "не отправлено: {}".format(e)


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Сервис работает. Откройте /docs, чтобы проверить эндпоинты."}


@app.post("/analyze_text")
def analyze_text(req: TextRequest) -> Dict[str, Any]:
    """Анализ текста конкурента."""
    try:
        result = openai_service.analyze_text(req.text, req.source or "")
    except Exception as e:
        raise _fail(e)
    history.add("text", req.source or "текст", result)
    return result


@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...), source: str = Form("")) -> Dict[str, Any]:
    """Анализ изображения (скриншот лендинга, баннер)."""
    data = await file.read()
    mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "image/png"
    try:
        result = openai_service.analyze_image(data, mime, source or (file.filename or ""))
    except Exception as e:
        raise _fail(e)
    history.add("image", source or (file.filename or "изображение"), result)
    return result


@app.post("/parse_demo")
def parse_demo(req: ParseRequest) -> Dict[str, Any]:
    """Открывает сайт в Safari, забирает текст и анализирует его."""
    try:
        page = parse_page(req.url, req.name or "")
        result = openai_service.analyze_text(page_to_prompt_text(page), req.name or req.url)
    except Exception as e:
        raise _fail(e)
    history.add("parse", req.name or req.url, result)
    return {"page": {k: page[k] for k in ("url", "title", "h1", "screenshot")}, "analysis": result}


@app.post("/analyze_data")
def analyze_data(send_to_telegram: bool = False) -> Dict[str, Any]:
    """Анализирует все скриншоты из папки data/ (имя файла = название конкурента)."""
    if not os.path.isdir(config.DATA_DIR):
        raise HTTPException(status_code=404, detail="Папка data/ не найдена")
    files = sorted(f for f in os.listdir(config.DATA_DIR) if f.lower().endswith(IMAGE_EXTENSIONS))
    if not files:
        raise HTTPException(status_code=404, detail="В папке data/ нет изображений")
    results = []  # type: List[Dict[str, Any]]
    for name in files:
        path = os.path.join(config.DATA_DIR, name)
        mime = mimetypes.guess_type(name)[0] or "image/png"
        source = os.path.splitext(name)[0]
        with open(path, "rb") as f:
            data = f.read()
        try:
            result = openai_service.analyze_image(data, mime, source)
        except Exception as e:
            result = {"error": "{}: {}".format(type(e).__name__, e)}
        history.add("image", source, result)
        results.append({"source": source, "result": result})
    return {"count": len(results), "results": results, "telegram": _maybe_send(results, send_to_telegram)}


@app.post("/parse_competitors")
def parse_competitors(send_to_telegram: bool = False) -> Dict[str, Any]:
    """Обходит сайты конкурентов из config.py (по одному, в Safari) и анализирует их."""
    results = []  # type: List[Dict[str, Any]]
    for name, url in config.COMPETITORS.items():
        try:
            page = parse_page(url, name)
            result = openai_service.analyze_text(page_to_prompt_text(page), name)
        except Exception as e:
            result = {"error": "{}: {}".format(type(e).__name__, e)}
        history.add("parse", name, result)
        results.append({"source": name, "url": url, "result": result})
    return {"count": len(results), "results": results, "telegram": _maybe_send(results, send_to_telegram)}


@app.get("/history")
def get_history() -> List[Dict[str, Any]]:
    """История запросов (последние записи из history.json)."""
    return history.load()
