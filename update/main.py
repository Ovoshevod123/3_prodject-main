import asyncio
from aiogram import Bot, Dispatcher, types
from hand import rt
from reply import rt_2
from feedback import rt_3
from admin import rt_4
from pay import rt_5
from ref import rt_6
from new_member import rt_7
from bot_cmds import private
from inf import TOKEN

BOT_TOKEN = TOKEN
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(rt, rt_2, rt_3, rt_4, rt_5, rt_6, rt_7)

async def main():
    global Message, Bot
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, skip_updates=True)

asyncio.run(main())