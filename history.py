"""Простая история запросов в файле history.json (последние N записей)."""
import json
import os
from datetime import datetime
from typing import Any, Dict, List

import config


def load() -> List[Dict[str, Any]]:
    if not os.path.exists(config.HISTORY_FILE):
        return []
    try:
        with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def add(kind: str, source: str, result: Dict[str, Any]) -> None:
    items = load()
    items.append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "kind": kind,  # text / image / parse
            "source": source,
            "result": result,
        }
    )
    items = items[-config.MAX_HISTORY_ITEMS:]
    with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
