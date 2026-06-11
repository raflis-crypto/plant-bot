import os
import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


@router.message(Command("info"))
async def handle_info(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /info <название растения>")
        return

    name = parts[1].strip()
    await message.answer("⏳ Ищу информацию...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/info", json={"name": name}
        ) as resp:
            if resp.status != 200:
                await message.answer("Ошибка при получении справки. Попробуйте позже.")
                return
            data = await resp.json()

    await message.answer(f"📖 <b>{name}</b>\n\n{data['text']}", parse_mode="HTML")
