"""Настройки проекта: ключи из .env, список конкурентов, описание нашего сайта."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- ProxyAPI (OpenAI-совместимый) ---
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "")
PROXY_API_BASE_URL = "https://api.proxyapi.ru/openai/v1"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Папки и файлы ---
DATA_DIR = "data"                # сюда кладём скриншоты лендингов конкурентов
SCREENSHOTS_DIR = "screenshots"  # сюда парсер сохраняет скриншоты сайтов
HISTORY_FILE = "history.json"
MAX_HISTORY_ITEMS = 30

# --- Парсинг (Selenium + Safari) ---
PAGE_LOAD_TIMEOUT = 30   # секунд на загрузку страницы
PAGE_RENDER_PAUSE = 4    # пауза, чтобы страница дорисовалась
MAX_TEXT_CHARS = 6000    # сколько текста страницы отправляем модели

# --- Конкуренты: название -> адрес сайта (поправьте под себя) ---
COMPETITORS = {
    "Daria AI": "https://dariabot.ru/",
    "Komanda.ai": "https://komanda.ai/beauty-salon",
    "AI Beauty Bot": "https://ai-beauty.bot/",
    "Jivo ИИ": "https://www.jivo.ru/blog/announcements/ii-dlja-salona-krasoty.html",
}

# --- Наш сайт: точка отсчёта для сравнения ---
# ПРОВЕРЬТЕ И ПОПРАВЬТЕ этот текст, чтобы он точно описывал ваши услуги.
MY_SITE_NAME = "Allo Beauty"
MY_SITE_URL = "https://allo-beauty.ru/"
MY_SITE_DESCRIPTION = (
    "Allo Beauty (allo-beauty.ru) — ИИ для салонов красоты и бьюти-мастеров: "
    "автоматизация и сопровождение. Строим ИИ-агентов на заказ, например "
    "ИИ-администратора, финансового консультанта и SMM-агента. "
    "Связаться можно в Telegram и VK."
)
