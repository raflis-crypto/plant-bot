import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import identify, info, recipe

load_dotenv(Path(__file__).parent.parent / ".env")
BOT_TOKEN = os.environ["BOT_TOKEN"]


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(identify.router)
    dp.include_router(info.router)
    dp.include_router(recipe.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
