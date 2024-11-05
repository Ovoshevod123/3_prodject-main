from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import asyncio
from datetime import date
from reply import buttons
from inf import GROUP

rt_3 = Router()
fb_score_main = 0

async def text_def(id_of, user):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{id_of}'")
    name = cur.fetchall()
    db.commit()
    db.close()

    if name[0][5] == 'None':
        price = ''
    else:
        if name[0][5].isdigit() == True:
            price = f"<b>{name[0][5]} ₽</b>\n"
        else:
            price = f"<b>{name[0][5]}</b>\n"
    group = name[0][7].split('|')
    group.pop(-1)
    gr = ''
    for i in group:
        gr = gr + f"#{i} "
    average = await average_rating(name[0][8])
    text = (f"<b>«{name[0][3]}»</b>\n"
            f"{price}"
            f"{name[0][4]}\n"
            f"{name[0][6]} 📍\n\n"
            f"@{name[0][8]}\n"
            f"<a href='t.me/Second_Vaps_bot/?start=2_{user}'>{average[0]} ({average[1]})</a> {'⭐' * round(average[0])}{' ☆' * (5 - round(average[0]))}\n\n"
            f"{gr}\n"
            f"ID: {name[0][1]}")
    return text

async def average_rating(user):
    common = 0
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT fb_score FROM fb_offer WHERE seller = '{user}'")
    score = cur.fetchall()
    col = len(score)
    db.commit()
    db.close()
    if col == 0:
        return 0, 0
    else:
        for i in score:
            common += int(i[0])
        common = round(int(common)/col, 2)
        return common, col

async def forward_fb(message, id):
    try:
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{id}'")
        name = cur.fetchone()
        db.commit()
        db.close()
        a = name[0]
        a = a.split('|')
        a.pop(0)
        text = await text_def(id, message.chat.username)
        builder = MediaGroupBuilder(caption=text)
        for i in a:
            builder.add_photo(media=f'{i}', parse_mode="HTML")
        await message.answer_media_group(media=builder.build())
        return id
    except:
        return 'error'

class feedback_class_1(StatesGroup):
    id = State()

class feedback_class_2(StatesGroup):
    text_fb = State()
    score = State()

class fb_chek(StatesGroup):
    user_name = State()

async def account_fb(call, msg):
    global fb_score, fbs
    rows = [[InlineKeyboardButton(text='<', callback_data='<<'), InlineKeyboardButton(text='>', callback_data='>>')],
            [InlineKeyboardButton(text='‹ Назад', callback_data='account')]]
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM fb_offer WHERE seller = '{msg.chat.username}'")
    fbs = cur.fetchall()
    db.commit()
    db.close()
    fb_score = len(fbs)
    await fbs_def(call.message, fbs, 0, 'acc')

@rt_3.callback_query(F.data == 'fb_back_1')
@rt_3.callback_query(F.data == 'fb_menu')
async def menu_fb(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='Оставить отзыв', callback_data='send_fb')],
            [InlineKeyboardButton(text='Посмотреть отзывы', callback_data='chek_fb')],
            [buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='📄 <b>Это меню отзывов.</b>\n\n'
                                      'Здесь можно посмотреть рейтинг и отзывы других пользователей, а также оставить свой отзыв на продавца.', reply_markup=markup, parse_mode="HTML")
    await state.clear()

@rt_3.callback_query(F.data == 'chek_fb')
async def feedback_chek_0(call: CallbackQuery, state: FSMContext):
    global fb_score_main
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Введите имя пользователя, без @\n\n'
                                      '(Пример: @name)', reply_markup=markup)
    await state.set_state(fb_chek.user_name)
    fb_score_main -= fb_score_main

@rt_3.callback_query(F.data == '>>')
async def feedback_chek_1(call: CallbackQuery):
    global fb_score_main
    fb_score_main += 1
    scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'acc')

@rt_3.callback_query(F.data == '<<')
async def feedback_chek_2(call: CallbackQuery):
    global fb_score_main
    if fb_score_main == 0:
        scr = fb_score_main
    else:
        fb_score_main -= 1
        scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'acc')

@rt_3.callback_query(F.data == '>')
async def feedback_chek_3(call: CallbackQuery):
    global fb_score_main
    fb_score_main += 1
    scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'fb')

@rt_3.callback_query(F.data == '<')
async def feedback_chek_4(call: CallbackQuery):
    global fb_score_main
    if fb_score_main == 0:
        scr = fb_score_main
    else:
        fb_score_main -= 1
        scr = fb_score_main
    await fbs_def(call.message, fbs, scr, 'fb')

async def fbs_def(message, data_fbs, score, out):
    if fb_score == 0:
        if out == 'fb':
            rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='chek_fb')]]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            await message.answer(text='У этого пользователя пока что нет отзывов', reply_markup=markup)
        else:
            rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='account')]]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            await message.edit_text(text='У вас пока что нету отзывов', reply_markup=markup)
    else:
        frst = 0
        for i in data_fbs:
            frst += int(i[3])
        srznch = round(frst/int(len(data_fbs)), 2)
        date = str(data_fbs[score][5]).split('-')
        date = f"{date[2]}.{date[1]}.{date[0]}"
        text = (f"<b>@{data_fbs[score][1]}</b> {srznch} ({fb_score})\n"
                f"<a href='t.me/Second_Vaps_TLT/{data_fbs[score][0]}'>Объявление</a>\n\n"
                f"{'⭐' * data_fbs[score][3]}{' ☆' * (5 - data_fbs[score][3])}\n"
                f"<b>Комментарий:</b>\n{data_fbs[score][2]}\n\n"
                f"<b>{date}</b>\n\n")
        if out == 'fb':
            rows = [[InlineKeyboardButton(text='<', callback_data='<'), InlineKeyboardButton(text=f'{score+1}/{fb_score}', callback_data='sfdgfdgdsf'), InlineKeyboardButton(text='>', callback_data='>')],
                    [InlineKeyboardButton(text='‹ Назад', callback_data='fb_menu')]]
            if fb_score == 1:
                for i in range(2):
                    rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == 0:
                rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == fb_score - 1:
                rows[0].pop(2)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
        else:
            rows = [[InlineKeyboardButton(text='<', callback_data='<<'), InlineKeyboardButton(text=f'{score+1}/{fb_score}', callback_data='sfdgfdgdsf'),InlineKeyboardButton(text='>', callback_data='>>')],
                    [InlineKeyboardButton(text='‹ Назад', callback_data='account')]]
            if fb_score == 1:
                for i in range(2):
                    rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == 0:
                rows[0].pop(0)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            elif score == fb_score - 1:
                rows[0].pop(2)
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=rows)

        try:
            await message.edit_text(text=text, reply_markup=markup, parse_mode='HTML' ,disable_web_page_preview=True)
        except:
            await message.answer(text=text, reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)

async def feedback_chek_group(message: Message, name):
    global fb_score, fbs
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM fb_offer WHERE seller = '{name}'")
    fbs = cur.fetchall()
    db.commit()
    db.close()
    fb_score = len(fbs)
    await fbs_def(message, fbs, 0, 'fb')

@rt_3.message(fb_chek.user_name)
async def feedback_chek_5(message: Message, state: FSMContext):
    global fb_score, data_fb, fbs
    await state.update_data(user_name=message.text)
    data_fb = await state.get_data()
    data_fb = data_fb['user_name']
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM fb_offer WHERE seller = '{data_fb}'")
    fbs = cur.fetchall()
    db.commit()
    db.close()
    fb_score = len(fbs)
    await fbs_def(message, fbs, 0, 'fb')
    await state.clear()

@rt_3.callback_query(F.data == 'send_fb')
async def feedback_1(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Введите ID объявления', reply_markup=markup)
    await state.clear()
    await state.set_state(feedback_class_1.id)

async def feedback_1_2(message, state):
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='fb_back_1')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text='Введите ID объявления', reply_markup=markup)
    await state.clear()
    await state.set_state(feedback_class_1.id)

@rt_3.message(feedback_class_1.id)
async def feedback_2(message: Message, state: FSMContext):
    global deff
    await state.update_data(id=message.text)
    data = await state.get_data()

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT offer_id_channel,seller FROM users_offer WHERE offer_id_channel = '{data['id']}'")
    db_var = cur.fetchall()
    cur.execute(f"SELECT fb_user FROM fb_offer WHERE offer_id = '{data['id']}'")
    db_var_2 = cur.fetchone()
    db.commit()
    db.close()
    if db_var_2 != None:
        await state.clear()
        await message.answer('❌ Вы уже оставляли отзыв на это объявление')
        await feedback_1_2(message, state)
    else:
        if db_var == []:
            await state.clear()
            await message.answer(text='❌ Объявление не найдено')
            await feedback_1_2(message, state)
        elif db_var[0][1] == message.chat.username:
            await message.answer('❌ Вы не можете оставить отзыв на самого себя')
            await feedback_1_2(message, state)
        else:
            deff = await forward_fb(message, data['id'])
            await message.answer(text='❗Убедитесь что верно выбрано объявление❗\n\n'
                                         'Напишите комментарий')
            await state.set_state(feedback_class_2.text_fb)

@rt_3.message(feedback_class_2.text_fb)
async def feedback_3(message: Message, state: FSMContext):
    await state.update_data(text_fb=message.text)
    rows = [[InlineKeyboardButton(text='1', callback_data='fb_1'), InlineKeyboardButton(text='2', callback_data='fb_2')],
            [InlineKeyboardButton(text='3', callback_data='fb_3'), InlineKeyboardButton(text='4', callback_data='fb_4')],
            [InlineKeyboardButton(text='5', callback_data='fb_5')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text='Поставьте оценку от 1 до 5', reply_markup=markup)

@rt_3.callback_query(F.data == 'fb_1')
@rt_3.callback_query(F.data == 'fb_2')
@rt_3.callback_query(F.data == 'fb_3')
@rt_3.callback_query(F.data == 'fb_4')
@rt_3.callback_query(F.data == 'fb_5')
async def feedback_4(call: CallbackQuery, state: FSMContext):
    global data, msg
    score = call.data.replace('fb_', '')
    rows = [[InlineKeyboardButton(text='Опубликовать', callback_data='publish_yes')],
            [InlineKeyboardButton(text='Заполнить отзыв заново', callback_data='send_fb')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    msg = call.message
    await state.update_data(score=score)
    data = await state.get_data()
    await call.message.edit_text(text=f"⬇️ Ваш отзыв\n\n"
                              f"{'⭐' * int(score)}{' ☆' * (5 - int(score))}\n\n"
                              f"<b>Комментарий:</b>\n"
                              f"{data['text_fb']}\n", reply_markup=markup, parse_mode="html")
    await state.clear()

@rt_3.callback_query(F.data == 'publish_yes')
async def fb_data_4_1(call: CallbackQuery, bot: Bot, state: FSMContext):
    msg_2 = await call.message.edit_text('📢 Отзыв опубликован')
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f'SELECT seller FROM users_offer WHERE offer_id_channel = "{data['id']}"')
    seller = cur.fetchone()
    cur.execute(f"INSERT INTO fb_offer VALUES ('{data['id']}', '{seller[0]}', '{data['text_fb']}', '{data['score']}', '{msg.from_user.id}', '{date.today()}')")
    db.commit()
    db.close()
    await start_def(call.message)
    await asyncio.sleep(3)
    await msg_2.delete()
    await state.clear()

async def start_def(message: Message):
    rows = [[buttons[5], buttons[1]],
            [buttons[6], buttons[8]],
            [buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text=f'<b>💨 Vaps Bot 💨</b>\n\n'\
            f'Покупайте, продавайте, обменивайте <i><b>POD-системы(подики)</b></i>, <i><b>жидкости</b></i>, все <i><b>расходники</b></i> для POD-систем и другое <b><a href="{GROUP}">здесь</a></b>'
            , reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)
