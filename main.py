import asyncio
from aiogram import Bot, Dispatcher, types
from hand import rt
from reply import rt_2
from feedback import rt_3
from admin import rt_4
from pay import rt_5
from ref import rt_6
from bot_cmds import private
from inf import TOKEN, ADMIN_LIST
from aiogram.client.session.aiohttp import AiohttpSession

BOT_TOKEN = TOKEN
# session = AiohttpSession(proxy='http://proxy.server:3128')
# bot = Bot(token=BOT_TOKEN, session=session)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(rt, rt_2, rt_3, rt_4, rt_5, rt_6)

async def main():
    global Message, Bot
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

asyncio.run(main())