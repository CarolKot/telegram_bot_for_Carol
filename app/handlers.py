from aiogram import F, Router
from aiogram.types import Message, Voice, Document, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.generate import ai_genetate
import time
import speech_recognition as sr
import pdfplumber
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import json

router = Router()

# Клавиатура с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Помощь"), KeyboardButton(text="⚙ Настройки")],
        [KeyboardButton(text="🔄 Перезапустить бота"), KeyboardButton(text="➕ Добавить пользователя")]
    ],
    resize_keyboard=True
)

# Файл для хранения разрешённых пользователей
ALLOWED_USERS_FILE = "allowed_users.json"

# Загружаем разрешённых пользователей из файла
try:
    with open(ALLOWED_USERS_FILE, "r") as f:
        ALLOWED_USERS = set(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    ALLOWED_USERS = {71316975}  # Начальный список разрешённых пользователей

# Храним время последнего запроса
user_last_request = {}

class Gen(StatesGroup):
    wait = State()
    add_user = State()

# Функция для сохранения разрешённых пользователей в файл
def save_allowed_users():
    with open(ALLOWED_USERS_FILE, "w") as f:
        json.dump(list(ALLOWED_USERS), f)

# ✅ Исправленный обработчик /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return
    await message.answer("👋 Добро пожаловать! Выберите действие:", reply_markup=keyboard)

# ✅ Добавление пользователя
@router.message(lambda message: message.text == "➕ Добавить пользователя")
async def ask_user_id(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ У вас нет доступа к этой функции.")
        return
    await state.set_state(Gen.add_user)
    await message.answer("✍ Введите ID пользователя, которого хотите добавить:")

@router.message(Gen.add_user)
async def add_user(message: Message, state: FSMContext):
    try:
        new_user_id = int(message.text)
        if new_user_id in ALLOWED_USERS:
            await message.answer("⚠️ Этот пользователь уже добавлен.")
        else:
            ALLOWED_USERS.add(new_user_id)
            save_allowed_users()
            await message.answer(f"✅ Пользователь {new_user_id} добавлен и сохранён в коде!")
    except ValueError:
        await message.answer("⚠️ Неверный формат ID. Введите числовой ID пользователя.")
    finally:
        await state.clear()

# ✅ Исправленный обработчик сообщений
@router.message()
async def generating(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ Доступ запрещён.")
        return
    
    if not message.text:
        await message.answer("⚠️ Пожалуйста, отправьте текстовое сообщение.")
        return
    
    if message.text.startswith("/"):
        await message.answer("⚠️ Команды не поддерживаются.")
        return

    if len(message.text) > 500:
        await message.answer("⚠️ Слишком длинный запрос. Уменьшите текст.")
        return

    now = time.time()
    last_request = user_last_request.get(message.from_user.id, 0)
    if now - last_request < 10:
        await message.answer("⏳ Подождите 10 секунд перед следующим запросом.")
        return

    user_last_request[message.from_user.id] = now

    await state.set_state(Gen.wait)
    response = await ai_genetate(message.from_user.id, message.text)  # Теперь используем правильную функцию
    await message.answer(response)
    await state.clear()

# ✅ Обработчик голосовых сообщений
@router.message(Voice)
async def handle_voice(message: Message, bot: Bot):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return

    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "voice.ogg")

    recognizer = sr.Recognizer()
    with sr.AudioFile("voice.ogg") as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="ru-RU")

    await message.answer(f"🎤 Вы сказали: {text}")

# ✅ Обработчик загрузки документов
@router.message(Document)
async def handle_document(message: Message, bot: Bot):
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return

    file = await bot.get_file(message.document.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "document.pdf")

    text = ""
    with pdfplumber.open("document.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    await message.answer(f"📄 Текст из документа:\n{text[:4096]}")
