import asyncio

from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
import datetime
from datetime import date
import pytz
import sqlite3
from hand import del_media,text_def
from inf import ADMIN_LIST, CHANNEL_ID, REPLY_TO

rt_4 = Router()

tz = pytz.timezone("Europe/Samara")

class ban_user(StatesGroup):
    username = State()

class anban_user(StatesGroup):
    username = State()

class del_of(StatesGroup):
    id = State()

class plus(StatesGroup):
    username = State()
    col = State()

@rt_4.message(Command('admin'))
async def chek_admin(message: Message, state: FSMContext):
    await state.clear()
    rows = [[InlineKeyboardButton(text='Запуск авто-постинга', callback_data='ap')],
            [InlineKeyboardButton(text='Бан пользователя', callback_data='ban')],
            [InlineKeyboardButton(text='Разбан пользователя', callback_data='anban')],
            [InlineKeyboardButton(text='Удалить объявление', callback_data='del_of')],
            [InlineKeyboardButton(text='Начислить дуплонов', callback_data='plus_balance')],
            [InlineKeyboardButton(text='output db', callback_data='db')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    if message.chat.id == ADMIN_LIST:
        await message.answer(text='Добро пожаловать', reply_markup=markup)

@rt_4.callback_query(F.data == 'ap')
async def auto_posting(call: CallbackQuery, bot: Bot):
    while True:
        # if int(datetime.datetime.now(tz).time().hour) == int(datetime.datetime.now(tz).time().hour):
        if int(datetime.datetime.now(tz).time().hour) == 7:
            db = sqlite3.connect('users.db')
            cur = db.cursor()
            cur.execute(f"SELECT offer_id_channel, final, seller FROM auto_posting")
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
                if still_time.days < 0:
                    db = sqlite3.connect('users.db')
                    cur = db.cursor()
                    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {i[0]}")
                    db.commit()
                    db.close()
                else:
                    await send_media(call, bot, i[0], i[2])
            await bot.send_message(chat_id=ADMIN_LIST, text='Все объявления опубликованы')
            await asyncio.sleep(82800)
        await asyncio.sleep(600)

async def send_media(call, bot, offer_id, seller):
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
    text = await text_def(offer_id, seller)
    text = text.split('ID: ', 1)[0]
    col = len(a)
    if col > 1:
        media = [
            types.InputMediaPhoto(media=a[0], caption=text, parse_mode='html'),
            *[types.InputMediaPhoto(media=photo_id) for photo_id in a[1:]]
        ]
    else:
        media = [types.InputMediaPhoto(media=a[0], caption=text, parse_mode='html')]
    send_02 = await bot.send_media_group(chat_id=CHANNEL_ID, media=media, reply_to_message_id=REPLY_TO)
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=send_02[0].message_id, caption=text + f'ID: {send_02[0].message_id}', parse_mode='html')
    await asyncio.sleep(5)

    await del_media(call, bot, offer_id)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM auto_posting WHERE offer_id_channel = '{offer_id}'")
    name_2 = cur.fetchall()
    name_2 = name_2[0]
    cur.execute(f"DELETE from users_offer WHERE offer_id_channel = {offer_id}")
    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {offer_id}")
    cur.execute(f"INSERT INTO users_offer VALUES ('{name[0]}', '{send_02[0].message_id}', '{name[2]}', '{name[3]}', '{name[4]}', '{name[5]}', '{name[6]}', '{name[7]}', '{name[8]}', '{name[9]}', '{name[10]}')")
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

@rt_4.callback_query(F.data == 'anban')
async def ban_2(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Введите username пользователя')
    await state.set_state(anban_user.username)

@rt_4.message(anban_user.username)
async def anban(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    data = await state.get_data()
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"DELETE from ban_users WHERE username = '{data['username']}'")
    db.commit()
    db.close()
    await message.answer('Пользователь разбанен')

@rt_4.callback_query(F.data == 'del_of')
async def del_of_1(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Введите id объявления')
    await state.set_state(del_of.id)

@rt_4.message(del_of.id)
async def del_of_2(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"DELETE from users_offer WHERE offer_id_channel = '{data['id']}'")
    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = '{data['id']}'")
    db.commit()
    db.close()
    await message.answer(text='Объявление удалено из баз')

@rt_4.callback_query(F.data == 'plus_balance')
async def plus_1(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Отправьте username')
    await state.set_state(plus.username)

@rt_4.message(plus.username)
async def plus_2(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('Отправьте на сколько увеличить баланс')
    await state.set_state(plus.col)

@rt_4.message(plus.col)
async def plus_3(message: Message, state: FSMContext):
    await state.update_data(col=message.text)
    data = await state.get_data()
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT balance FROM users WHERE username = '{data['username']}'")
    balance = cur.fetchone()
    cur.execute(f"UPDATE users SET balance= {int(balance[0]) + int(data['col'])} WHERE username = '{data['username']}'")
    db.commit()
    db.close()
    await message.answer('Дуплоны зачислены')
    await state.clear()

@rt_4.callback_query(F.data == 'db')
async def ex(call: CallbackQuery):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    name = cur.fetchall()
    for i in name:
        a = f'{i[0]}\n\n'
        cur.execute(f"SELECT * FROM {i[0]}")
        data = cur.fetchall()
        if data != []:
            for i in data:
                a = a + f"{i}\n\n".replace(',', '\n')
        await call.message.answer(text=f"{a}")
    db.commit()
    db.close()