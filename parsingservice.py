"""Парсинг сайтов конкурентов через Selenium и браузер Safari (macOS).

Перед первым запуском один раз:
  1) Safari -> Разработка -> Разрешить удалённую автоматизацию
  2) в Terminal: safaridriver --enable
"""
import os
import re
import time
from typing import Dict

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

import config


def _slug(name: str) -> str:
    return re.sub(r"[^0-9a-zA-Zа-яА-Я]+", "-", name).strip("-").lower() or "site"


def parse_page(url: str, name: str = "") -> Dict[str, str]:
    """Открывает страницу в Safari и возвращает title, h1 и видимый текст."""
    driver = None
    try:
        driver = webdriver.Safari()
        driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        driver.get(url)
        time.sleep(config.PAGE_RENDER_PAUSE)  # даём странице дорисоваться

        title = driver.title or ""
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except WebDriverException:
            h1 = ""
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except WebDriverException:
            body_text = ""
        body_text = re.sub(r"\n{3,}", "\n\n", body_text).strip()[: config.MAX_TEXT_CHARS]

        screenshot_path = ""
        try:
            os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)
            screenshot_path = os.path.join(config.SCREENSHOTS_DIR, _slug(name or url) + ".png")
            driver.save_screenshot(screenshot_path)
        except Exception:
            screenshot_path = ""

        return {
            "url": url,
            "title": title,
            "h1": h1,
            "text": body_text,
            "screenshot": screenshot_path,
        }
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


def page_to_prompt_text(page: Dict[str, str]) -> str:
    """Собирает данные страницы в один текст для модели."""
    return "Адрес: {}\nTitle: {}\nГлавный заголовок (h1): {}\n\nТекст страницы:\n{}".format(
        page["url"], page["title"], page["h1"], page["text"]
    )
