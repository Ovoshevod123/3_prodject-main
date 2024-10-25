import asyncio
from aiogram import Bot, Dispatcher, types
from sup_inf import TOKEN
from sup_hand import rt

BOT_TOKEN = TOKEN
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(rt)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())