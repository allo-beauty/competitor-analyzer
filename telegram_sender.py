"""Отправка отчёта в Telegram (токен и chat_id берутся из .env)."""
from typing import Any, Dict, List

import requests

import config


def send_message(text: str) -> None:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise RuntimeError("Не заданы TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в .env")
    url = "https://api.telegram.org/bot{}/sendMessage".format(config.TELEGRAM_BOT_TOKEN)
    # у Telegram лимит 4096 символов на сообщение
    for i in range(0, len(text), 3900):
        resp = requests.post(
            url,
            json={"chat_id": config.TELEGRAM_CHAT_ID, "text": text[i : i + 3900]},
            timeout=20,
        )
        if resp.status_code != 200:
            raise RuntimeError("Telegram не принял сообщение: {}".format(resp.text[:200]))


def _bullets(items: Any, limit: int = 3) -> str:
    if not isinstance(items, list):
        return ""
    return "\n".join("• {}".format(x) for x in items[:limit])


def format_report(results: List[Dict[str, Any]]) -> str:
    """Короткий отчёт по конкурентам для Telegram (без markdown)."""
    parts = ["Анализ конкурентов: {} шт., сравнение с {}".format(len(results), config.MY_SITE_NAME)]
    for item in results:
        r = item.get("result", {})
        if "error" in r:
            parts.append("{}: не удалось проанализировать ({})".format(item.get("source", "?"), r["error"]))
            continue
        block = [item.get("source", "?")]
        scores = []
        if "offer_clarity" in r:
            scores.append("понятность предложения {}/10".format(r["offer_clarity"]))
        if "automation_level" in r:
            scores.append("автоматизация {}/10".format(r["automation_level"]))
        if "visual_style_score" in r:
            scores.append("визуал {}/10".format(r["visual_style_score"]))
        if scores:
            block.append("Оценки: " + ", ".join(scores))
        if r.get("summary"):
            block.append(str(r["summary"]))
        vs = _bullets(r.get("vs_allo_beauty"))
        if vs:
            block.append("Сравнение с {}:\n{}".format(config.MY_SITE_NAME, vs))
        parts.append("\n".join(block))
    return "\n\n".join(parts)
