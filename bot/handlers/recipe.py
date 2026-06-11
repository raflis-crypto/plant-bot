import os
import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


@router.message(Command("recipe"))
async def handle_recipe(message: Message):
    # Ожидаемый формат: /recipe <растение> | <состояние>
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or "|" not in parts[1]:
        await message.answer(
            "Использование: /recipe <название растения> | <состояние>\n"
            "Например: /recipe Ромашка | простуда"
        )
        return

    plant_part, condition_part = parts[1].split("|", 1)
    name = plant_part.strip()
    condition = condition_part.strip()

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
