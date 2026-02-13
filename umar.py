import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from api_token import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== DATA ======

RESTAURANTS = {
    "NY": [
        {
            "name": "Halal Food NYC",
            "menu": "🍔 Burger\n🥙 Shawarma\n🍕 Pizza",
            "lat": 40.7128,
            "lon": -74.0060
        }
    ],
    "CA": [
        {
            "name": "Halal LA",
            "menu": "🍗 Chicken\n🥗 Salad\n🍔 Burger",
            "lat": 34.0522,
            "lon": -118.2437
        }
    ]
}

ratings = {}  # {"NY_0": [5,4,3]}

# ====== START ======

@dp.message(Command("start"))
async def start(message: Message):
    states_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="NY")],
            [KeyboardButton(text="CA")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Салом! Штатро интихоб кунед:",
        reply_markup=states_keyboard
    )

# ====== STATE SELECT ======

@dp.message(F.text.in_(RESTAURANTS.keys()))
async def choose_state(message: Message):
    state = message.text

    kb = InlineKeyboardBuilder()
    for idx, rest in enumerate(RESTAURANTS[state]):
        kb.button(
            text=rest["name"],
            callback_data=f"rest:{state}:{idx}"
        )

    kb.adjust(1)

    await message.answer(
        "Ресторанро интихоб кунед:",
        reply_markup=kb.as_markup()
    )

# ====== RESTAURANT VIEW ======

@dp.callback_query(F.data.startswith("rest:"))
async def show_restaurant(callback: CallbackQuery):
    _, state, idx = callback.data.split(":")
    idx = int(idx)

    restaurant = RESTAURANTS[state][idx]
    rest_id = f"{state}_{idx}"

    avg_rating = 0
    if rest_id in ratings and ratings[rest_id]:
        avg_rating = sum(ratings[rest_id]) / len(ratings[rest_id])

    text = (
        f"🍽 {restaurant['name']}\n"
        f"⭐ Рейтинг: {avg_rating:.1f}"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Меню", callback_data=f"menu:{state}:{idx}")
    kb.button(text="📍 Геолокация", callback_data=f"loc:{state}:{idx}")
    kb.button(text="🛒 Фармоиш", callback_data=f"order:{state}:{idx}")
    kb.button(text="⭐ Рейтинг диҳед", callback_data=f"rating:{state}:{idx}")
    kb.adjust(1)

    await callback.message.answer(text, reply_markup=kb.as_markup())
    await callback.answer()

# ====== MENU ======

@dp.callback_query(F.data.startswith("menu:"))
async def show_menu(callback: CallbackQuery):
    _, state, idx = callback.data.split(":")
    idx = int(idx)

    menu_text = RESTAURANTS[state][idx]["menu"]

    await callback.message.answer(f"📋 Меню:\n\n{menu_text}")
    await callback.answer()

# ====== LOCATION ======

@dp.callback_query(F.data.startswith("loc:"))
async def send_location(callback: CallbackQuery):
    _, state, idx = callback.data.split(":")
    idx = int(idx)

    restaurant = RESTAURANTS[state][idx]

    await bot.send_location(
        chat_id=callback.message.chat.id,
        latitude=restaurant["lat"],
        longitude=restaurant["lon"]
    )

    await callback.answer()

# ====== ORDER ======
@dp.callback_query(F.data.startswith("order:"))
async def order_menu(callback: CallbackQuery):
    _, state, idx = callback.data.split(":")
    idx = int(idx)

    restaurant = RESTAURANTS[state][idx]
    items = restaurant["menu"].split("\n")

    kb = InlineKeyboardBuilder()

    for item in items:
        kb.button(
            text=item,
            callback_data=f"buy:{state}:{idx}:{item}"
        )

    kb.adjust(1)

    await callback.message.answer(
        "Таомро интихоб кунед:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()
@dp.callback_query(F.data.startswith("buy:"))
async def confirm_order(callback: CallbackQuery):
    _, state, idx, item = callback.data.split(":", 3)

    await callback.message.answer(
        f"🛒 {item}\n\n"
        "✅ Фармоиши шумо қабул шуд!\n"
        "📞 Мо ба зудӣ бо шумо тамос мегирем."
    )
    await callback.answer()
# ====== RATING MENU ======

@dp.callback_query(F.data.startswith("rating:"))
async def rating_menu(callback: CallbackQuery):
    _, state, idx = callback.data.split(":")
    rest_id = f"{state}_{idx}"

    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.button(
            text=f"{i}⭐",
            callback_data=f"rate:{rest_id}:{i}"
        )
    kb.adjust(5)

    await callback.message.answer(
        "Баҳо диҳед (1-5 ⭐):",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# ====== SAVE RATING ======

@dp.callback_query(F.data.startswith("rate:"))
async def save_rating(callback: CallbackQuery):
    _, rest_id, value = callback.data.split(":")
    value = int(value)

    if rest_id not in ratings:
        ratings[rest_id] = []

    ratings[rest_id].append(value)

    avg = sum(ratings[rest_id]) / len(ratings[rest_id])

    await callback.message.answer(
        f"✅ Ташаккур!\n⭐ Рейтинги нав: {avg:.1f}"
    )
    await callback.answer()

# ====== RUN ======

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
