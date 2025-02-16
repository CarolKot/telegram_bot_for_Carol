# config

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токены из окружения
AI_TOKEN = os.getenv('AI_TOKEN')
TG_TOKEN = os.getenv('TG_TOKEN')

# Проверяем, загружены ли токены
if not AI_TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения AI_TOKEN не установлена!")

if not TG_TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения TG_TOKEN не установлена!")

# Вывод API-ключа для отладки (Но скрываем часть, чтобы не светить в логах)
print(f"AI_TOKEN загружен: {AI_TOKEN[:10]}********")
print(f"TG_TOKEN загружен: {TG_TOKEN[:10]}********")

