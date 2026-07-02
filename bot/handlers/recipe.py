import os
import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from handlers.identify import user_plants

router = Router()
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


@router.message(Command("recipe"))
async def handle_recipe(message: Message):
    # Формат: /recipe <болезнь>
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "Использование: /recipe <болезнь>\n"
            "Например: /recipe простуда\n\n"
            "Сначала пришли фото растения — я запомню его для рецепта."
        )
        return

    condition = parts[1].strip()
    name = user_plants.get(message.from_user.id)

    if not name:
        await message.answer("Сначала пришли фото растения.")
        return

    await message.answer("⏳ Составляю рецепт...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/recipe",
            json={"name": name, "condition": condition},
        ) as resp:
            if resp.status != 200:
                await message.answer("Ошибка при составлении рецепта. Попробуйте позже.")
                return
            data = await resp.json()

    await message.answer(
        f"🌿 <b>Рецепт: {name}</b> при «{condition}»\n\n{data['text']}",
        parse_mode="HTML",
    )
