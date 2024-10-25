from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import asyncio
from sup_inf import CHANNEL_ID

rt = Router()

class question(StatesGroup):
    question = State()

@rt.message(Command('start'))
async def start_def(message: Message):
    await message.answer(text=f'Это бот тех. поддержки\n\n'
                              f'Просто напиши свой вопрос и он автоматически отправится администратору')

@rt.message(Command('answer'))
async def answer_def(message: Message, bot: Bot):
    if message.text == '/answer':
        pass
    else:
        data = (message.text).split(maxsplit=2)
        chat_id = data[1]
        text = data[2]
        await bot.send_message(chat_id=int(chat_id), text="✉️ Ответ от тех. поддержки:\n\n"
                                                          f"{text}")
        await message.answer(text='✉️ Ответ отправлен')

@rt.message()
async def question_def(message: Message, bot: Bot):
    text = message.text
    text = (f'Вопрс от пользователя @{message.chat.username}\n\n'
            f'Вопрос:\n'
            f'{text}\n\n'
            f'<code>/answer {message.chat.id} Ваш ответ</code>')
    if message.photo != None:
        photo = message.photo
        await bot.send_photo(chat_id=CHANNEL_ID, photo=photo[0].file_id, caption=text, parse_mode="HTML")
    else:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
    await message.answer(text='✉️ Вопрос отправлен')
