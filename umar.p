import json
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from api_token import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ---------- LOAD JSON ----------
with open("restaurants.json", "r", encoding="utf-8") as f:
    RESTAURANTS = json.load(f)

# ---------- STATE KEYBOARD ----------
def states_keyboard():
    buttons = [KeyboardButton(text=state) for state in RESTAURANTS.keys()]
    return ReplyKeyboardMarkup(
        keyboard=[buttons[i:i+3] for i in range(0, len(buttons), 3)],
        resize_keyboard=True
    )

# ---------- INLINE BUTTONS ----------
def restaurant_buttons(state, index):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Rating",
                    callback_data=f"rating|{state}|{index}"
                ),
                InlineKeyboardButton(
                    text="📋 Menu",
                    callback_data=f"menu|{state}|{index}"
                ),
                InlineKeyboardButton(
                    text="📍 Location",
                    callback_data=f"loc|{state}|{index}"
                )
            ]
        ]
    )

# ---------- START ----------
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "🇺🇸 <b>Welcome to EatHalalUSA</b>\n\nSelect a state:",
        reply_markup=states_keyboard()
    )

# ---------- SHOW RESTAURANTS ----------
@dp.message()
async def show_restaurants(message: types.Message):
    state = message.text.upper()

    if state not in RESTAURANTS:
        await message.answer("❌ Такого штата нет.")
        return

    for index, rest in enumerate(RESTAURANTS[state]):
        text = (
            f"🍽 <b>{rest['name']}</b>\n"
            f"📞 {rest['phone']}\n"
            f"📍 {rest['address']}"
        )

        await message.answer(
            text,
            reply_markup=restaurant_buttons(state, index)
        )

# ---------- CALLBACK HANDLER ----------
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    action, state, index = callback.data.split("|")
    index = int(index)

    rest = RESTAURANTS[state][index]

    if action == "rating":
        await callback.message.answer(
            f"⭐ <b>Rating:</b> {rest['rating']}"
        )

    elif action == "menu":
        menu_text = "📋 <b>Menu:</b>\n"
        for item in rest.get("menu", []):
            menu_text += f"• {item}\n"

        await callback.message.answer(menu_text)

    elif action == "loc":
        if rest.get("lat") and rest.get("lon"):
            await callback.message.answer_location(
                latitude=rest["lat"],
                longitude=rest["lon"]
            )
        else:
            await callback.message.answer("📍 Location not available.")

    await callback.answer()

# ---------- RUN ----------
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
