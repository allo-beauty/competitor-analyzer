# Мониторинг конкурентов для Allo Beauty

ИИ-анализатор рынка конкурентов в нише «ИИ-администраторы и автоматизация для салонов красоты».
Берёт тексты и скриншоты сайтов конкурентов, анализирует их через модель (ProxyAPI) и сравнивает с сайтом Allo Beauty.

## Что умеет
- `POST /analyze_text` — анализ текста конкурента
- `POST /analyze_image` — анализ скриншота или баннера
- `POST /parse_demo` — открывает сайт в Safari (Selenium), забирает текст и анализирует
- `POST /parse_competitors` — обходит все сайты из `config.py`
- `POST /analyze_data` — анализирует все скриншоты из папки `data/`
- `GET /history` — история запросов (`history.json`)
- Параметр `send_to_telegram=true` отправляет короткий отчёт в Telegram

В ответе есть собственные поля оценки: `offer_clarity` (понятность предложения, 0-10),
`automation_level` (глубина автоматизации, 0-10), `visual_style_score` (визуал, 0-10)
и `vs_allo_beauty` (чем конкурент отличается от Allo Beauty).

## Запуск (macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # впишите свои ключи в .env
uvicorn run:app --reload
```
Откройте http://127.0.0.1:8000/docs и проверяйте эндпоинты кнопкой Try it out.

Для парсинга: Safari → Разработка → «Разрешить удалённую автоматизацию», затем один раз `safaridriver --enable`.

## Структура
- `run.py` — FastAPI-приложение
- `openaiservice.py` — промпты и вызовы модели
- `parsingservice.py` — парсинг сайтов через Selenium
- `telegram_sender.py` — отправка отчёта в Telegram
- `history.py` — история запросов
- `config.py` — настройки, список конкурентов, описание нашего сайта
- `data/` — скриншоты конкурентов (имя файла = название конкурента)

## Безопасность
Ключи хранятся только в `.env`, файл добавлен в `.gitignore` и в репозиторий не попадает.

## Кейс
_Заполнить на шаге 5: ниша, 4-5 конкурентов, какие поля оценки придуманы и зачем, главные выводы._
