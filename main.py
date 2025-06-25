import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import openai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Пример базы растений
PLANT_DB = {
    "подорожник": {"status": "✅ Можно", "note": "Успокаивает пищеварение."},
    "лук": {"status": "❌ Нельзя", "note": "Токсичен для кроликов."},
    "тысячелистник": {"status": "⚠️ Ограниченно", "note": "Давать понемногу."}
}

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне фото растения, и я скажу, можно ли его давать кролику 🐇🌿")

@dp.message()
async def handle_photo(message: Message):
    if not message.photo:
        await message.answer("Пожалуйста, отправь фотографию растения.")
        return

    photo = message.photo[-1]
    photo_file = await bot.download(photo)
    photo_path = "plant.jpg"
    with open(photo_path, "wb") as f:
        f.write(photo_file.read())

    with open(photo_path, "rb") as image_file:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Определи растение на фото и скажи, можно ли его давать кролику."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_file.read().encode('base64').decode()}"}}
                    ],
                }
            ],
            max_tokens=1000,
        )

    content = response["choices"][0]["message"]["content"]

    found = None
    for name in PLANT_DB:
        if name.lower() in content.lower():
            found = name
            break

    if found:
        status = PLANT_DB[found]["status"]
        note = PLANT_DB[found]["note"]
        await message.answer(f"🌱 Это: <b>{found.capitalize()}</b>
{status} — {note}")
    else:
        await message.answer("❓ Не смог определить растение или оно не в базе. Будь осторожна!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))