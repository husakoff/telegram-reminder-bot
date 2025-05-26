
import os
import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Загружаем ID пользователей из users.json
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = []

# Сохраняем список пользователей
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
        save_users()
    await message.answer("Привет! Я буду напоминать тебе проверить расписание каждый день в 9:00 ☀️")

@dp.callback_query_handler(lambda c: c.data == "viewed")
async def confirm_viewed(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text="Спасибо! Ты подтвердил просмотр ✅")

# Ежедневная рассылка
async def send_reminders():
    for user_id in users:
        try:
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton("Просмотрел ✅", callback_data="viewed")
            )
            await bot.send_message(user_id, "Проверь расписание на сегодня в EasyWeek 👀", reply_markup=keyboard)
        except Exception as e:
            print(f"Ошибка отправки {user_id}: {e}")

# Планировщик
scheduler = AsyncIOScheduler()
scheduler.add_job(send_reminders, "cron", hour=9, minute=0)
scheduler.start()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
