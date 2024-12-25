from aiogram import Router, Bot
from aiogram.types import Message, ChatJoinRequest

rt_7 = Router()

# @rt_7.message(Command('id'))
# async def id(message: Message):
#     await message.answer(f'{message.chat.id}')

@rt_7.chat_join_request()
async def test(chat_join: ChatJoinRequest, bot: Bot):
    await bot.send_message(chat_id=chat_join.from_user.id, text='👋 Привет! Я бот Vape барахолки.\n\n'
                                                                'С помощью меня ты можешь:\n'
                                                                '— <b>Публиковать объявления</b> в нашей группе\n'
                                                                '— <b>Оставлять/просматривать отзывы</b> на продавцов\n'
                                                                '— <b>Удобно перемещаться</b> между своими объявлениями и <b>редактировать</b> их внутри бота \n\n'
                                                                '✨ Отправь команду <b>/start</b> и попробуй сам\n', parse_mode='html')
    await chat_join.approve()