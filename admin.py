import asyncio
from os.path import isabs

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import datetime
from datetime import date
import pytz
import sqlite3
from hand import average_rating, del_media, use_token_ub
from inf import ADMIN_LIST, CHANNEL_ID

rt_4 = Router()

tz = pytz.timezone("Europe/Samara")

class ban_user(StatesGroup):
    username = State()

@rt_4.message(Command('admin'))
async def chek_admin(message: Message):
    rows = [[InlineKeyboardButton(text='Запуск авто-постинга', callback_data='ap')],
            [InlineKeyboardButton(text='Бан пользователя', callback_data='ban')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if message.chat.id == ADMIN_LIST:
        await message.answer(text='Добро пожаловать', reply_markup=markup)

@rt_4.callback_query(F.data == 'ap')
async def auto_posting(call: CallbackQuery, bot: Bot):
    while True:
        if int(datetime.datetime.now(tz).time().hour) == 9 and int(datetime.datetime.now(tz).time().minute) == 0:
        # if int(datetime.datetime.now(tz).time().hour) == int(datetime.datetime.now(tz).time().hour):
            db = sqlite3.connect('users.db')
            cur = db.cursor()
            cur.execute(f"SELECT offer_id_channel, final FROM auto_posting")
            ids = cur.fetchall()
            cur.execute(f"SELECT id, date FROM unblock")
            ids_2 = cur.fetchall()
            db.commit()
            db.close()
            for i in ids_2:
                still_time = i[1].split('-')
                still_time = datetime.datetime(int(still_time[0]), int(still_time[1]), int(still_time[2]), tzinfo=tz) - datetime.datetime.now(tz)
                if still_time.days == 29:
                    db = sqlite3.connect('users.db')
                    cur = db.cursor()
                    cur.execute(f"DELETE from unblock WHERE id = {i[0]}")
                    db.commit()
                    db.close()
            for i in ids:
                still_time = i[1].split('-')
                still_time = datetime.datetime(int(still_time[0]), int(still_time[1]), int(still_time[2]), tzinfo=tz) - datetime.datetime.now(tz)
                if still_time.days + 1 < 0:
                    db = sqlite3.connect('users.db')
                    cur = db.cursor()
                    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {i[0]}")
                    db.commit()
                    db.close()
                else:
                    await send_media(bot, i[0])
            await asyncio.sleep(82800)
        await asyncio.sleep(30)

async def send_media(bot, offer_id):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{offer_id}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    name = name[0]
    a = name[2]
    a = a.split('|')
    a.pop(0)
    average = await average_rating(name[8])
    text = f"Цена: {name[5]}\n{name[3]}\n{name[4]}\n{name[6]}\n\nПродавец: @{name[8]}\nРейтинг продавца: {average[0]}\nКол-во отзывов: {average[1]}"
    col = len(a)
    if col > 1:
        media = [
            types.InputMediaPhoto(media=a[0], caption=text),
            *[types.InputMediaPhoto(media=photo_id) for photo_id in a[1:]]
        ]
    else:
        media = [types.InputMediaPhoto(media=a[0], caption=text)]
    send_02 = await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=send_02[0].message_id, caption=text + f'\nid сообщения: {send_02[0].message_id}')

    await del_media(bot, offer_id)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM auto_posting WHERE offer_id_channel = '{offer_id}'")
    name_2 = cur.fetchall()
    name_2 = name_2[0]
    cur.execute(f"DELETE from users_offer WHERE offer_id_channel = {offer_id}")
    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {offer_id}")
    cur.execute(f"INSERT INTO users_offer VALUES ('{name[0]}', '{send_02[0].message_id}', '{name[2]}', '{name[3]}', '{name[4]}', '{name[5]}', '{name[6]}', '{name[7]}', '{name[8]}')")
    cur.execute(f"INSERT INTO auto_posting VALUES ('{name_2[0]}', '{send_02[0].message_id}', '{name_2[2]}', '{name_2[3]}', '{name_2[4]}')")
    db.commit()
    db.close()

@rt_4.callback_query(F.data == 'ban')
async def auto_posting(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Введите username пользователя')
    await state.set_state(ban_user.username)

@rt_4.message(ban_user.username)
async def ban_1(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    data = await state.get_data()
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT id FROM users WHERE username = '{data['username']}'")
    id_user = cur.fetchone()
    cur.execute(f"INSERT INTO ban_users VALUES ('{id_user[0]}', '{data['username']}', '{date.today()}')")
    db.commit()
    db.close()
    await message.answer('Пользователь забанен')