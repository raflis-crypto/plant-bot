import os
import aiohttp
from aiogram import Router
from aiogram.types import Message, PhotoSize

router = Router()
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# user_id -> последнее определённое название растения
user_plants: dict[int, str] = {}


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message):
    photo: PhotoSize = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            image_bytes = await resp.read()

        form = aiohttp.FormData()
        form.add_field("file", image_bytes, filename="photo.jpg", content_type="image/jpeg")

        async with session.post(f"{BACKEND_URL}/identify", data=form) as resp:
            if resp.status != 200:
                await message.answer("Ошибка при распознавании. Попробуйте ещё раз.")
                return
            result = await resp.json()

    if result["name"] is None:
        score_pct = int(result["score"] * 100)
        await message.answer(
            f"🌿 Растение не определено уверенно (уверенность {score_pct}%).\n"
            f"Попробуйте сфотографировать крупнее или с другого ракурса."
        )
        return

    name = result["name"]
    score_pct = int(result["score"] * 100)

    # Сохраняем растение для этого пользователя
    user_plants[message.from_user.id] = name

    # Запрашиваем описание сразу
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BACKEND_URL}/info", json={"name": name}) as resp:
            if resp.status == 200:
                info_data = await resp.json()
                info_text = info_data["text"]
            else:
                info_text = "⚠️ Не удалось загрузить описание.\n\n⚠️ Информация носит справочный характер. Перед применением проконсультируйтесь со специалистом."

    await message.answer(
        f"🌱 <b>{name}</b>\n"
        f"<i>{result['sci']}</i> · Уверенность: {score_pct}%\n\n"
        f"{info_text}\n\n"
        f"💊 Чтобы получить рецепт, отправьте:\n<code>/recipe ваша болезнь</code>",
        parse_mode="HTML",
    )
