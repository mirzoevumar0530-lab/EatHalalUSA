import json
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from api_token import BOT_TOKEN

# Лог
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
router = Router()

# --------- Загрузка JSON ----------
def load_data():
    try:
        with open("restaurants.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("restaurants.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --------- Клавиатура штатов ----------
def states_keyboard(data):
    buttons = [KeyboardButton(text=state) for state in data.keys()]
    return ReplyKeyboardMarkup(
        keyboard=[buttons[i:i+3] for i in range(0, len(buttons), 3)],
        resize_keyboard=True
    )

# --------- START ----------
@router.message(CommandStart())
async def start(message: types.Message):
    data = load_data()
    await message.answer(
        "🇺🇸 <b>Welcome to USA Halal Guide</b>\n\nВыберите штат:",
        reply_markup=states_keyboard(data)
    )

# --------- Выбор штата ----------
@router.message()
async def show_restaurants(message: types.Message):
    data = load_data()
    state = message.text.upper()

    if state not in data:
        await message.answer("❌ Такого штата нет.")
        return

    restaurants = data[state]

    if not restaurants:
        await message.answer("❌ В этом штате пока нет ресторанов.")
        return

    for r in restaurants:
        rating = r.get("rating", 0)
        stars = "⭐" * int(rating)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⭐ Оценить",
                        callback_data=f"rate_{state}_{r['name']}"
                    )
                ]
            ]
        )

        text = (
            f"🍽 <b>{r['name']}</b>\n"
            f"📍 {r['address']}\n"
            f"📞 {r['phone']}\n"
            f"{stars}\n"
        )

        await message.answer(text, reply_markup=keyboard)

# --------- Кнопка оценить ----------
@router.callback_query(F.data.startswith("rate_"))
async def rate_restaurant(callback: types.CallbackQuery):
    _, state, name = callback.data.split("_", 2)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐1", callback_data=f"setrate_{state}_{name}_1"),
                InlineKeyboardButton(text="⭐2", callback_data=f"setrate_{state}_{name}_2"),
                InlineKeyboardButton(text="⭐3", callback_data=f"setrate_{state}_{name}_3"),
                InlineKeyboardButton(text="⭐4", callback_data=f"setrate_{state}_{name}_4"),
                InlineKeyboardButton(text="⭐5", callback_data=f"setrate_{state}_{name}_5"),
            ]
        ]
    )

    await callback.message.answer("Выберите рейтинг:", reply_markup=keyboard)
    await callback.answer()

# --------- Установка рейтинга ----------
@router.callback_query(F.data.startswith("setrate_"))
async def set_rating(callback: types.CallbackQuery):
    _, state, name, rating = callback.data.split("_", 3)
    rating = int(rating)

    data = load_data()

    for r in data[state]:
        if r["name"] == name:
            r["rating"] = rating

    save_data(data)

    await callback.message.answer("✅ Рейтинг сохранен!")
    await callback.answer()

# --------- Запуск ----------
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Bot started...")
    asyncio.run(main())
