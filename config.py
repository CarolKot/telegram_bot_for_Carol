# config

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

AI_TOKEN = os.getenv('AI_TOKEN')
TG_TOKEN = os.getenv('TG_TOKEN')

# Проверяем, загружены ли токены
if not AI_TOKEN or not TG_TOKEN:
    raise ValueError("❌ Ошибка: переменные окружения AI_TOKEN и TG_TOKEN не установлены!")



# AI_TOKEN = os.getenv('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')
# TG_TOKEN = os.getenv('7646171185:AAGJPJVM8THzcu0Hh3rj90GVdixL9iOp_SY')