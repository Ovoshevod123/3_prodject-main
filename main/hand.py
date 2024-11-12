import datetime
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import asyncio
from reply import buttons, but_del, edit_but, buttons_edit
from inf import CHANNEL_ID, REPLY_TO, GROUP
from feedback import average_rating, account_fb, feedback_chek_group

rt = Router()

photo = []
id_list = []
id_list_dispatch = []
id_list_auto = []
chek_ub = []
edit_list = []
group = []
rows_new_1 = [[InlineKeyboardButton(text='POD-система (Подик)', callback_data='POD_система')],
              [InlineKeyboardButton(text='Жидкость', callback_data='Жидкость')],
              [InlineKeyboardButton(text='Картридж/испаритель/бак', callback_data='Картридж_испаритель_бак')],
              [InlineKeyboardButton(text='Одноразовая электронная сигарета',callback_data='Одноразовая_электронная_сигарета')],
              [InlineKeyboardButton(text='Другое', callback_data='Другое')],
              [buttons[4]]]

main_text = f'<b>💨 Vaps Bot 💨</b>\n\n'\
            f'Покупайте / продавайте / обменивайте <i><b>POD-системы(подики)</b></i>, <i><b>жидкости</b></i>, все <i><b>расходники</b></i> для POD-систем и другое <b><a href="{GROUP}">здесь</a></b>'

class new_product(StatesGroup):
    group = State()
    photo = State()
    name = State()
    description = State()
    price = State()
    locate = State()

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
            f"ID: {name[0][1]}\n\n"
            f"<b><a href='t.me/Second_Vaps_bot/?start'>Объявления публикуются с помощью бота</a></b>")
    return text

async def start_def(message: Message):
    edit_list.clear()
    try:
        await msg_photo.delete()
        await msg_2.delete()
        await edit_msg.delete()
    except:
        pass
    rows = [[buttons[5], buttons[1]],
            [buttons[6], buttons[8]],
            [buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer(text=main_text, reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)

@rt.message(Command(commands=['start', 'menu']), F.chat.type == 'private')
async def start(message: Message, bot: Bot):
    edit_list.clear()
    try:
        await msg_photo.delete()
        await msg_2.delete()
    except:
        pass
    rows = [[buttons[5], buttons[1]],
            [buttons[6], buttons[8]],
            [buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT id FROM users WHERE id = '{message.chat.id}'")
    info = cur.fetchone()
    if message.text in ['/start', '/menu']:
        ref = None
        await message.answer(text=main_text, reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)
    else:
        ref = message.text.replace('/start ', '')
        if ref[0:2] == '2_':
            ref = ref.replace('2_', '')
            await feedback_chek_group(message, ref)
        elif ref[0:2] == '1_':
            ref = ref.replace('1_', '')
            cur.execute(f"SELECT id FROM users WHERE id = {message.chat.id}")
            user = cur.fetchall()
            if user == []:
                cur.execute(f"SELECT id FROM users WHERE id = '{ref}'")
                cur.execute(f"SELECT col_ref FROM users WHERE id = '{ref}'")
                col_ref = cur.fetchall()
                cur.execute(f"SELECT balance FROM users WHERE id = '{ref}'")
                balance = cur.fetchall()
                cur.execute(f"Update users set 'col_ref' = '{int(col_ref[0][0]) + 1}' where id = '{ref}'")
                cur.execute(f"Update users set balance = {int(balance[0][0]) + 50} where id = {ref}")
                await bot.send_message(chat_id=int(ref), text='🎉 Поздравляем!\n'
                                                              'У вас новый реферальный пользователь.\n'
                                                              f'На ваш баланс начислено 50₽\n\n'
                                                              f'Ваших рефералов теперь {int(col_ref[0][0]) + 1}\n')
            else:
                ref = None
            await message.answer(text=main_text, reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)
    if info == None:
        if ref == None:
            cur.execute(f"INSERT INTO users VALUES ('{message.chat.id}', '{message.chat.username}', '0', '0', 'None')")
        else:
            cur.execute(f"INSERT INTO users VALUES ('{message.chat.id}', '{message.chat.username}', '0', '0', '{ref}')")
    db.commit()
    db.close()

@rt.callback_query(F.data == 'back')
async def back(call: CallbackQuery, state: FSMContext):
    global id_list, id_list_pay
    rows = [[buttons[5], buttons[1]],
            [buttons[6], buttons[8]],
            [buttons[0]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text=main_text, reply_markup=markup, parse_mode='HTML', disable_web_page_preview=True)
    await state.clear()
    id_list.clear()
    id_list_dispatch.clear()
    id_list_auto.clear()

# @rt.callback_query(F.data == 'new')
# async def new_1(callback: CallbackQuery, state: FSMContext):
#     rows = [[InlineKeyboardButton(text='Под система', callback_data='pod'), InlineKeyboardButton(text='Жидкость', callback_data='zhizha')],
#             [buttons[4]]]
#     markup = InlineKeyboardMarkup(inline_keyboard=rows)
#     photo.clear()
#     db = sqlite3.connect('users.db')
#     cur = db.cursor()
#     cur.execute(f"SELECT id FROM unblock WHERE id = '{send_01.from_user.id}'")
#     ub = cur.fetchone()
#     cur.execute(f"SELECT col FROM unblock_col WHERE id = '{send_01.from_user.id}'")
#     col = cur.fetchone()
#     if col == None:
#         col = [0]
#     if ub == None:
#         cur.execute(f"SELECT date FROM users_offer WHERE id = '{send_01.from_user.id}'")
#         b = cur.fetchall()
#         date = datetime.datetime.now()
#         if b == None:
#             await callback.message.edit_text(text=f'Вы начали заполнение анкеты нового товара.\n\nВыбирете класс объявления:',
#                                              reply_markup=markup)
#         else:
#             loc = []
#             for i in b:
#                 if str(i[0]) == str(date.date()):
#                     loc.append(True)
#             if not loc:
#                 await callback.message.edit_text(text=f'Вы начали заполнение анкеты нового товара.\n\nВыбирете класс объявления:',
#                                                  reply_markup=markup)
#             else:
#                 rows_2 = [[InlineKeyboardButton(text='Использовать токен', callback_data='use_token_ub')]]
#                 markup = InlineKeyboardMarkup(inline_keyboard=rows_2)
#                 await callback.message.edit_text(f'Вы сегодня уже публиковали объявление\nУ вас {col[0]} токенов', reply_markup=markup)
#                 loc.clear()
#     else:
#         await callback.message.edit_text(text=f'Вы начали заполнение анкеты нового товара.\n\nВыбирете класс объявления:',
#                                          reply_markup=markup)
#     db.commit()
#     db.close()

@rt.callback_query(F.data == 'new') # была F.data == use_token_ub
async def use_token_ub(call: CallbackQuery, state: FSMContext):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT id FROM ban_users WHERE id = '{call.from_user.id}'")
    data = cur.fetchone()
    db.commit()
    db.close()
    if call.from_user.username != None:
        if data != None:
            await call.message.answer("Вам запрещена публикация объявлений из за нарушения правил барахолки")
        else:
            global chek_ub
            chek_ub.clear()
            rows = [[InlineKeyboardButton(text='POD-система (Подик)', callback_data='POD_система')],
                    [InlineKeyboardButton(text='Жидкость', callback_data='Жидкость')],
                    [InlineKeyboardButton(text='Картридж/испаритель/бак', callback_data='Картридж_испаритель_бак')],
                    [InlineKeyboardButton(text='Одноразовая электронная сигарета', callback_data='Одноразовая_электронная_сигарета')],
                    [InlineKeyboardButton(text='Другое', callback_data='Другое')],
                    [buttons[4]]]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            chek_ub.append(True)
            await call.message.edit_text(text=f'<b>Этап 1/6</b>\n\n'
                                              f'📣 Вы начали заполнение нового объявления\n\n'
                                              f'Выберите категории объявления:',reply_markup=markup, parse_mode='html')
    else:
        await call.message.delete()
        msg = await call.message.answer(text='У вас не введено имя пользователя, из за этого другие пользователи не смогут перейти в ваш профиль и написать вам.\n\n'
                                                      'Перейдите в настройки Telegram и введите имя пользователя.')
        await start_def(call.message)
        await asyncio.sleep(30)
        await msg.delete()

@rt.callback_query(F.data == 'POD_система')
@rt.callback_query(F.data == 'Жидкость')
@rt.callback_query(F.data == 'Картридж_испаритель_бак')
@rt.callback_query(F.data == 'Одноразовая_электронная_сигарета')
@rt.callback_query(F.data == 'Другое')
async def new_1(call: CallbackQuery):
    global rows_new_1
    for i in range(5):
        if call.data == rows_new_1[i][0].callback_data:
            if call.data not in group:
                if group == []:
                    rows_new_1.insert(5, [InlineKeyboardButton(text='Продолжить ›', callback_data='next')],)
                group.append(rows_new_1[i][0].callback_data)
                rows_new_1[i][0].text = f'• {rows_new_1[i][0].text} •'
            else:
                group.remove(call.data)
                rows_new_1[i][0].text = rows_new_1[i][0].text[1:-1]
                if group == []:
                    rows_new_1.pop(5)
            markup = InlineKeyboardMarkup(inline_keyboard=rows_new_1)
            await call.message.edit_text(text=f'<b>Этап 1/6</b>\n\n'
                                              f'📣 Вы начали заполнение нового объявления\n\n'
                                              f'Выберите категории объявления:',reply_markup=markup, parse_mode='html')

@rt.callback_query(F.data == 'next')
async def new_2_1(call: CallbackQuery, state: FSMContext):
    res = ''
    for i in group:
        res = res + i + '|'
    await state.update_data(group=res)
    await call.message.edit_text(text='<b>Этап 2/6</b>\n\n'
                                      'Пришлите фото', parse_mode='html')
    await state.set_state(new_product.photo)

@rt.message(new_product.photo)
async def new_2_2(message: Message, state: FSMContext):
    global msg_photo
    kb = [[types.KeyboardButton(text="Сохранить фото и продолжить")]]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    try:
        if message.text == 'Сохранить фото и продолжить':
            await state.update_data(photo=photo)
            await state.set_state(new_product.name)
            await message.answer(text='Фото сохранены.', reply_markup=types.ReplyKeyboardRemove())
            await message.answer(text='<b>Этап 3/6</b>\n\n'
                                      'Введите название товара', parse_mode='html')
        else:
            photo_1 = message.photo
            photo.append(photo_1[-1].file_id)
            col = len(photo)
            if col == 5:
                await message.answer(text='Фото добавлено – 5 из 5', reply_markup=types.ReplyKeyboardRemove())
                await message.answer(text='<b>Этап 3/6</b>\n\n'
                                          'Введите название товара', reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')
                while len(photo) > 5:
                    photo.pop()
                await state.update_data(photo=photo)
                await state.set_state(new_product.name)
            elif col > 5:
                # await message.answer(text='Вы отправили больше 5 фото')
                pass
            else:
                msg_photo = await message.answer(text=f'Фото добавлено – {col} из 5\nЕще одно?', reply_markup=markup)
    except TypeError:
        await message.answer(text='Пришлите фото!')

@rt.message(new_product.name)
async def new_3(message: Message, state: FSMContext):
    global msg_2
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(name=message.text)
        await state.set_state(new_product.price)
        kb = [[types.KeyboardButton(text="Пропустить")]]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        msg_2 = await message.answer(text='<b>Этап 4/6</b>\n\n'
                                          'Введите цену товара', reply_markup=markup, parse_mode='html')

@rt.message(new_product.price)
async def new_5(message: Message, state: FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(price=message.text)
        await state.set_state(new_product.description)
        await message.answer(text='<b>Этап 5/6</b>\n\n'
                                  'Введите описание товара', reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')

@rt.message(new_product.description)
async def new_4(message: Message, state: FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(description=message.text)
        await state.set_state(new_product.locate)
        await message.answer(text='<b>Этап 6/6</b>\n\n'
                                  'Укажите место встречи с покупателем', parse_mode='html')

@rt.message(new_product.locate)
async def new_6(message: Message, state: FSMContext, bot: Bot, ):
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(locate=message.text)
        data = await state.get_data()
        global text, send, name_ofer, data_state
        data_state = data
        average = await average_rating(message.chat.username)
        if data['price'] == 'Пропустить':
            data['price'] = None
            price = ''
        else:
            if data['price'].isdigit() == True:
                price = f"<b>{data['price']} ₽</b>\n"
            else:
                price = f"<b>{data['price']}</b>\n"
        gr = ''
        for i in group:
            gr = gr + f"#{i} "
        text = (f"<b>«{data['name']}»</b>\n"
                f"{price}"
                f"{data['description']}\n"
                f"{data['locate']} 📍\n\n"
                f"@{message.chat.username}\n"
                f"<a href='t.me/Second_Vaps_bot/?start=2_{message.chat.username}'>{average[0]} ({average[1]})</a> {'⭐' * round(average[0])}{' ☆' * (5 - round(average[0]))}\n\n"
                f"{gr}\n")
        builder = MediaGroupBuilder(caption=text)
        for i in data['photo']:
            builder.add_photo(media=f'{i}', parse_mode="HTML")
        send = await message.answer_media_group(media=builder.build())
        rows = [[buttons[3]],
                [buttons[2]]]
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(text='⬆️ Вот так будет выглядеть ваше объявление', reply_markup=markup)
        await state.clear()

@rt.callback_query(F.data == 'good')
async def send_0(callback: CallbackQuery, bot: Bot):
    global chek_ub

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    try:
        if chek_ub[0] == True:
            cur.execute(f"SELECT col FROM unblock_col WHERE id = '{callback.from_user.id}'")
            col = cur.fetchone()
            cur.execute(f"UPDATE unblock_col SET col = {int(col[0] - 1)} WHERE id = '{callback.from_user.id}'")
    except:
        pass

    col = len(photo)
    if col > 1:
        media = [
            types.InputMediaPhoto(media=photo[0], caption=text, parse_mode="HTML"),
            *[types.InputMediaPhoto(media=photo_id) for photo_id in photo[1:]]
        ]
    else:
        media = [types.InputMediaPhoto(media=photo[0], caption=text, parse_mode="HTML")]

    send_02 = await bot.send_media_group(chat_id=CHANNEL_ID, media=media, reply_to_message_id=REPLY_TO)
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=send_02[0].message_id, caption=text + f'ID: {send_02[0].message_id}\n\n'
                                                                                                        f'<b><a href="t.me/Second_Vaps_bot/?start">Объявления публикуются с помощью бота</a></b>', parse_mode="HTML")

    a = ''
    for i in data_state['photo']:
        a = a+'|'+i

    date = datetime.datetime.now()
    cur.execute(
        f"""INSERT INTO users_offer VALUES ('{callback.message.chat.id}', '{send_02[0].message_id}', '{a}', '{data_state['name']}', '{data_state['description']}', '{data_state['price']}', '{data_state['locate']}', '{data_state['group']}', '{callback.message.chat.username}', '{date.date()}', '{date.time().hour}:{date.time().minute}')""")
    cur.execute(f"SELECT username FROM users WHERE id = '{callback.message.chat.id}'")
    chek_username = cur.fetchone()
    if str(chek_username[0]) == 'None':
        cur.execute(f"UPDATE users SET username = '{callback.message.chat.username}' WHERE id = '{callback.message.chat.id}'")
    db.commit()
    db.close()

    a = await callback.message.edit_text(
        text=f'Ваше объявление опубликовано <a href="{GROUP}/{send_02[0].message_id}">здесь</a>.',
        parse_mode='HTML',disable_web_page_preview=True)
    await start_def(callback.message)
    await asyncio.sleep(10)
    await a.delete()
    photo.clear()

async def offer_def(msg, from_var):
    global id_list, id_list_dispatch, id_list_auto

    deff = but_del(msg, from_var)
    if from_var == 'menu':
        for i in deff[1].keys():
            id_list.append(f'{i[0]}_menu')

    if from_var == 'dispatch':
        for i in deff[1].keys():
            id_list_dispatch.append(f'{i[0]}_dispatch')

    if from_var == 'auto':
        for i in deff[1].keys():
            id_list_auto.append(f'{i[0]}_auto')
    row = deff[0]
    return row

@rt.callback_query(F.data == 'account')
async def account(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Ваши отзывы', callback_data='stat'), buttons[7]],
            [InlineKeyboardButton(text='Реферальная система', callback_data='ref')],
            [buttons[4]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE id = '{call.message.chat.id}'")
    date = cur.fetchall()
    cur.execute(f"SElECT balance FROM users WHERE id = '{call.message.chat.id}'")
    balance = cur.fetchone()
    db.commit()
    db.close()
    col = len(date)
    average = await average_rating(call.message.chat.username)
    await call.message.edit_text(text=
                                f'👤 <b>Личный кабинет</b>\n\n'
                                f'💰 <b>Баланс: </b>{int(balance[0])} ₽\n\n'
                                f'📣 <b>Количество объявлений: </b>{col}\n\n'
                                f'🏆 <b>Рейтинг:  </b>{average[0]} ({average[1]}) {'\u2B50' * round(average[0])}{' ☆' * (5 - round(average[0]))}'
                                 , reply_markup=markup, parse_mode='HTML')

@rt.callback_query(F.data == 'stat')
async def account(call: CallbackQuery):
    await account_fb(call, call.message)

@rt.callback_query(F.data == 'my_off')
async def delete_0(call: CallbackQuery):
    rows = await offer_def(call.message, 'menu')
    rows_2 = [[buttons[0]],
              [InlineKeyboardButton(text='‹ Назад', callback_data='account')]]
    if len(rows) == 1:
        markup = InlineKeyboardMarkup(inline_keyboard=rows_2)
        await call.message.edit_text(text='У вас нет активных объявлений.\n\nХотите создать новое объявление?', reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        await call.message.edit_text(text='⬇️ <b>Это ваши объявления</b>\n\n'
                                          'Здесь можно <i><b>удалить</b></i> или <i><b>отредактировать</b></i> ваше объявление', reply_markup=markup, parse_mode='html')

async def forward(message, offer_data):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{offer_data}'")
    name = cur.fetchone()
    db.commit()
    db.close()
    a = name[0]
    a = a.split('|')
    a.pop(0)
    text = await text_def(offer_data, message.chat.username)
    text = text.replace('Объявления публикуются с помощью бота', '')
    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}', parse_mode="HTML")
    id_msg = await message.answer_media_group(media=builder.build())
    return id_msg

async def del_media(call, bot, id_offer):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{id_offer}'")
    photo_ = cur.fetchone()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{id_offer}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    photo_ = photo_[0]
    photo_ = photo_.split('|')
    photo_.pop(0)
    col = len(photo_)
    if name[0][5] == 'None':
        price = ''
    else:
        if name[0][5].isdigit() == True:
            price = f"<b>{name[0][5]} ₽</b>\n"
        else:
            price = f"<b>{name[0][5]}</b>\n"
    try:
        for i in range(col):
            ii = int(id_offer) + col - 1
            ii = ii - i
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=ii)
    except:
        try:
            average = await average_rating(name[0][8])
            text = (f"<b>❗ ЭТО ОБЪЯВЛЕНИЕ УДАЛЕННО ❗</b>\n\n"
                    f"«🗑DEL<b>{name[0][3]}</b>DEL🗑»\n"
                    f"{price}"
                    f"{name[0][4]}\n"
                    f"{name[0][6]} 📍\n\n"
                    f"@{name[0][8]}\n"
                    f"<a href='t.me/Second_Vaps_bot/?start=2_{call.from_user.username}'>{average[0]} ({average[1]})</a> {'⭐' * round(average[0])}{' ☆' * (5 - round(average[0]))}\n\n"
                    f"#{name[0][7]}\n"
                    f"ID: {name[0][1]}")
            await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=id_offer, caption=text, parse_mode="HTML")
        except Exception as e:
            print(e)

@rt.callback_query(lambda query: query.data in id_list)
async def delete_1(call: CallbackQuery, bot: Bot):
    global call_data, call_inf, id_msg_2, id_list
    await call.message.delete()
    id_list.clear()
    call_data = call.data
    call_data = call_data.replace('_menu', '')
    call_inf = call
    id_msg_2 = await forward(call.message, call_data)
    rows = [[edit_but[0], edit_but[1]],
            [edit_but[2]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.answer(text='⬆️ Это ваше объявление\n\nЧто хотите сделать?', reply_markup=markup)

@rt.callback_query(F.data == 'back_2')
async def back_edit(call: CallbackQuery, bot: Bot):
    await delete_0(call)

@rt.callback_query(F.data == 'sell')
async def del_1(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Да', callback_data='yes'), InlineKeyboardButton(text='Нет', callback_data='no')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Вы уверены что хотите удалить объявление', reply_markup=markup)

@rt.callback_query(F.data == 'dell')
async def del_1(call: CallbackQuery):
    rows = [[InlineKeyboardButton(text='Да', callback_data='del_yes'), InlineKeyboardButton(text='Нет', callback_data='del_no')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='Вы уверены что хотите удалить объявление?', reply_markup=markup)

@rt.callback_query(F.data == 'del_yes')
async def back_edit(call: CallbackQuery, bot: Bot):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{call_data}'")
    photo_ = cur.fetchone()
    cur.execute(f"DELETE from users_offer WHERE offer_id_channel = {call_data}")
    cur.execute(f"DELETE from auto_posting WHERE offer_id_channel = {call_data}")
    db.commit()
    db.close()
    photo_ = photo_[0]
    photo_ = photo_.split('|')
    photo_.pop(0)

    if name[0][5] == 'None':
        price = ''
    else:
        if name[0][5].isdigit() == True:
            price = f"<b>{name[0][5]} ₽</b>\n"
        else:
            price = f"<b>{name[0][5]}</b>\n"

    col = len(photo_)
    try:
        for i in range(col):
            ii = int(call_data) + col-1
            ii = ii - i
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=ii)
    except:
        average = await average_rating(name[0][8])
        text = (f"<b>❗ ЭТО ОБЪЯВЛЕНИЕ УДАЛЕННО ❗</b>\n\n"
                f"«🗑DEL<b>{name[0][3]}</b>DEL🗑»\n"
                f"{price}"
                f"{name[0][4]}\n"
                f"{name[0][6]} 📍\n\n"
                f"@{name[0][8]}\n"
                f"<a href='t.me/Second_Vaps_bot/?start=2_{call.from_user.username}'>{average[0]} ({average[1]})</a> {'⭐' * round(average[0])}{' ☆' * (5 - round(average[0]))}\n\n"
                f"ID: {name[0][1]}")
        await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=call_data, caption=text, parse_mode="HTML")

    msg_del = await call.message.edit_text(text='🗑️ Объявление удалено')
    await start_def(call.message)
    await asyncio.sleep(5)
    await msg_del.delete()

@rt.callback_query(F.data == 'del_no')
async def back_edit(call: CallbackQuery):
    rows = [[edit_but[0], edit_but[1]],
            [edit_but[2]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='⬆️ Это ваше объявление\n\n'
                                      'Что хотите сделать?', reply_markup=markup)

@rt.callback_query(F.data == 'edit')
async def edit_0(call: CallbackQuery):
    rows = [[buttons_edit[0]],
            [buttons_edit[2]],
            [buttons_edit[1]],
            [buttons_edit[3]],
            [buttons_edit[4]],
            [buttons_edit[5]]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(text='⬆️ Это ваше объявление\n\n'
                                      'Здесь вы можете изменить его.\n'
                                      'Что хотите изменить?', reply_markup=markup)

class edit_product(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    locate = State()

async def edit_def(a, b, c):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"Update users_offer set {a} = '{b}' where offer_id_channel = '{c}'")
    db.commit()
    db.close()

async def edit_media(message: Message, photo):
    a = photo.split('|')
    a.pop(0)
    text = await text_def(call_data, message.chat.username)
    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}', parse_mode="HTML")
    b = await message.answer_media_group(media=builder.build())
    return a, b

@rt.callback_query(F.data == 'photo')
async def edit_photo(call: CallbackQuery, state: FSMContext, bot: Bot):
    global col_photos
    photo.clear()
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='edit')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT photo FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    col_photos = name[0][0].split('|')
    col_photos.pop(0)
    col_photos = len(col_photos)
    db.commit()
    db.close()

    await call.message.edit_text(text=f'Пришлите до {col_photos} новых фото:', reply_markup=markup)
    await state.set_state(edit_product.photo)

async def search(a):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    data = cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{a}'")
    db.commit()
    db.close()
    return data

@rt.message(edit_product.photo)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    global send_media_msg, gl_data, edit_msg
    kb = [[types.KeyboardButton(text="Это все, сохранить фото")]]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_photo')],
           [types.InlineKeyboardButton(text="Заполнить заново", callback_data='photo')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)
    try:
        if message.text == 'Это все, сохранить фото':
            await state.update_data(photo=photo)
            data = await state.get_data()
            gl_data = data
            a = ''
            for i in data['photo']:
                a = a + '|' + i
            send_media_msg = await edit_media(message, a)
            await message.answer(text='⬆️ Вот так теперь выглядит ваше объявление', reply_markup=markup_2)
            await edit_msg.delete()
            await state.clear()
        else:
            photo_1 = message.photo
            photo.append(photo_1[-1].file_id)
            col = len(photo)
            if col == col_photos:
                await message.answer(text=f'Фото добавлено – {col_photos} из {col_photos}')
                while len(photo) > col_photos:
                    photo.pop()
                await state.update_data(photo=photo)
                data = await state.get_data()
                gl_data = data
                edit_photo_list = ''
                for i in data['photo']:
                    edit_photo_list = edit_photo_list + '|' + i
                send_media_msg = await edit_media(message, edit_photo_list)
                await message.answer(text='⬆️ Вот так теперь выглядит ваше объявление', reply_markup=markup_2)
                await edit_msg.delete()
                await state.clear()
            elif col > col_photos:
                pass
            else:
                edit_msg = await message.answer(text=f'Фото добавлено – {col} из {col_photos}. Еще одно?', reply_markup=markup)
    except TypeError:
        await message.answer(text='Пришлите фото!')

@rt.callback_query(F.data == 'edit_yes_photo')
async def edit_photo_2(call: CallbackQuery, bot: Bot):
    edit_photo_list = ''
    for i in gl_data['photo']:
        edit_photo_list = edit_photo_list + '|' + i
    # await edit_def('photo', edit_photo_list, call_data)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"Update users_offer set {'photo'} = '{edit_photo_list}' where offer_id_channel = '{call_data}'")
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchall()
    db.commit()
    db.close()
    text = await text_def(call_data, call.from_user.username)
    a = name[0][2]
    a = a.split('|')
    a.pop(0)
    iii = 0
    for photos in a:
        ii = int(call_data) + iii
        iii = iii + 1
        try:
            if ii == int(call_data):
                await bot.edit_message_media(media=InputMediaPhoto(media=photos, caption=text, parse_mode='html'), chat_id=CHANNEL_ID, message_id=ii)
            else:
                await bot.edit_message_media(media=InputMediaPhoto(media=photos, parse_mode='html'), chat_id=CHANNEL_ID, message_id=ii)
        except:
            pass
    del iii
    if len(a) < col_photos:
        for i in range(col_photos - len(a)):
            col = int(call_data) + int(col_photos) - 1 - i
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=col)

    a = await call.message.edit_text(text='✏️ Объявление изменено')
    await start_def(call.message)
    await asyncio.sleep(5)
    await a.delete()
    photo.clear()

@rt.callback_query(F.data == 'edit_yes_text')
async def edit_text(call: CallbackQuery, bot: Bot):
    print(edit_list)
    await edit_def(edit_list[0][0], edit_list[0][1], call_data)
    text = await text_def(call_data, call.from_user.username)
    await bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=call_data, caption=text, parse_mode="HTML")
    a = await call.message.edit_text(text='✏️ Объявление изменено')
    await start_def(call.message)
    await asyncio.sleep(3)
    await a.delete()

async def send_media(message, user, what_edit, edit):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users_offer WHERE offer_id_channel = '{call_data}'")
    offer = cur.fetchall()
    offer = list(offer[0])
    db.commit()
    db.close()
    a = offer[2]
    a = a.split('|')
    a.pop(0)
    if what_edit == 'name':
        offer[3] = edit
    if what_edit == 'price':
        offer[5] = edit
    if what_edit == 'description':
        offer[4] = edit
    if what_edit == 'locate':
        offer[6] = edit

    if offer[5] == 'None':
        price = ''
    else:
        if offer[5].isdigit() == True:
            price = f"<b>{offer[5]} ₽</b>\n"
        else:
            price = f"<b>{offer[5]}</b>\n"
    group = offer[7].split('|')
    group.pop(-1)
    gr = ''
    for i in group:
        gr = gr + f"#{i} "

    average = await average_rating(offer[8])
    text = (f"<b>«{offer[3]}»</b>\n"
            f"{price}"
            f"{offer[4]}\n"
            f"{offer[6]} 📍\n\n"
            f"@{offer[8]}\n"
            f"<a href='t.me/Second_Vaps_bot/?start=2_{user}'>{average[0]} ({average[1]})</a> {'⭐' * round(average[0])}{' ☆' * (5 - round(average[0]))}\n\n"
            f"{gr}\n"
            f"ID: {offer[1]}")

    builder = MediaGroupBuilder(caption=text)
    for i in a:
        builder.add_photo(media=f'{i}', parse_mode="HTML")
    await message.answer_media_group(media=builder.build())

@rt.callback_query(F.data == 'name')
async def edit_name(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='edit')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT offer_name FROM users_offer WHERE offer_id_channel = '{call_data}'")
    name = cur.fetchone()
    db.commit()
    db.close()
    await call.message.edit_text(text=f'Ваше старое название:\n'
                                      f'<code>{name[0]}</code>\n\n'
                                      f'Введите новое название товара',
                                 reply_markup=markup, parse_mode='html')
    await state.set_state(edit_product.name)

@rt.callback_query(F.data == 'description')
async def edit_description(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='edit')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT description FROM users_offer WHERE offer_id_channel = '{call_data}'")
    description = cur.fetchone()
    db.commit()
    db.close()

    await call.message.edit_text(text=f'Ваше старое описание:\n'
                                      f'<code>{description[0]}</code>\n\n'
                                      f'Введите новое описание товара',
                                 reply_markup=markup, parse_mode='html')
    await state.set_state(edit_product.description)

@rt.callback_query(F.data == 'price')
async def edit_price(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='edit')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(f"SELECT price FROM users_offer WHERE offer_id_channel = '{call_data}'")
    price = cur.fetchone()
    db.commit()
    db.close()
    await call.message.edit_text(text=f'Ваше старая цена:\n'
                                      f'<code>{price[0]}</code>\n\n'
                                      f'Введите новую цену товара',
                                 reply_markup=markup, parse_mode='html')
    await state.set_state(edit_product.price)

@rt.callback_query(F.data == 'locate')
async def edit_locate(call: CallbackQuery, state: FSMContext):
    rows = [[InlineKeyboardButton(text='‹ Назад', callback_data='edit')]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    await call.message.edit_text(text=f'Введите новое место встречи с покупателем',
                                 reply_markup=markup)
    await state.set_state(edit_product.locate)

@rt.message(edit_product.name)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    global edit_list
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')],
           [types.InlineKeyboardButton(text="Заполнить заново", callback_data='name')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(name=message.text)
        data = await state.get_data()
        edit_list.append(['offer_name', data['name']])
        await send_media(message, message.from_user.id, 'name', data['name'])
        await message.answer(text='⬆️ Вот так теперь выглядит ваше объявление', reply_markup=markup_2)
        await state.clear()

@rt.message(edit_product.description)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    global edit_list
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')],
           [types.InlineKeyboardButton(text="Заполнить заново", callback_data='description')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(description=message.text)
        data = await state.get_data()
        edit_list.append(['description', data['description']])
        await send_media(message, message.from_user.id, 'description', data['description'])
        await message.answer(text='⬆️ Вот так теперь выглядит ваше объявление', reply_markup=markup_2)
        await state.clear()

@rt.message(edit_product.price)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    global edit_list
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')],
           [types.InlineKeyboardButton(text="Заполнить заново", callback_data='price')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(price=message.text)
        data = await state.get_data()
        edit_list.append(['price', data['price']])
        await send_media(message, message.from_user.id, 'price', data['price'])
        await message.answer(text='⬆️ Вот так теперь выглядит ваше объявление', reply_markup=markup_2)
        await state.clear()

@rt.message(edit_product.locate)
async def edit_photo_2(message: Message, state: FSMContext, bot: Bot):
    global edit_list
    but = [[types.InlineKeyboardButton(text="Внести изменения", callback_data='edit_yes_text')],
           [types.InlineKeyboardButton(text="Заполнить заново", callback_data='locate')]]
    markup_2 = InlineKeyboardMarkup(inline_keyboard=but)
    if message.content_type != types.ContentType.TEXT:
        await message.answer(text='Пришлите текст!')
    else:
        await state.update_data(locate=message.text)
        data = await state.get_data()
        edit_list.append(['locate', data['locate']])
        await send_media(message, message.from_user.id, 'locate', data['locate'])
        await message.answer(text='⬆️ Вот так теперь выглядит ваше объявление', reply_markup=markup_2)
        await state.clear()

@rt.message(Command('chat'))
async def start(message: Message, bot: Bot):
    await message.answer(text=f'{message.chat.id}')