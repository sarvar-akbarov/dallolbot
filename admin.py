import traceback

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from config import (

    STATE_MAIN,

    STATE_ADMIN,
    STATE_SETTINGS,
    STATE_ADD,
    STATE_LOGIN,
    STATE_CHOOSE,

    TOKEN,

    PASSWORD_ADMIN
)

BTN_DEALS, BTN_CREATE, BTN_CHANGE = 'Deals', 'Create', 'Change'

attributes = {'name': 'Nomi', 'freelancer_id': 'Frilanser IDsi', 'client_id': 'Zakazchik ID si',
              'channel_link': 'Kanal limki', 'is_admin': 'Admin Qilish'}
from db_helper import DBHelper


def begin_conservation_btn(type):
    return [
        [
            InlineKeyboardButton('Boshlash', callback_data='begin-' + type)
        ]
    ]


def admin_buttons():
    return [
        [
            KeyboardButton(BTN_CREATE),
        ],
        [
            KeyboardButton(BTN_CHANGE)
        ],
    ]


def create_btns(attributes, data):
    btns = []
    q = True
    for key, value in attributes.items():
        if data.get(key) is not None:
            q = q and True
            symbol = ' ✅ '
        else:
            q = q and False
            symbol = ' ‼️'

        btns.append([
            InlineKeyboardButton(value + symbol, callback_data=key)
        ])
    if q:
        btns.append([
            InlineKeyboardButton('Saqlash', callback_data='save')
        ])

    btns.append([
        InlineKeyboardButton('Bekor qilish', callback_data='cancel')
    ])
    return btns


def chat_btns(chats):
    btns = []
    # print(chats)
    for chat in chats:
        btns.append([
            InlineKeyboardButton(chat['name'], callback_data=chat['id'])
        ])

    btns.append([
        InlineKeyboardButton('Bekor qilish', callback_data='cancel')
    ])
    return btns


def chat_setting_btns(id):
    return [
        [
            InlineKeyboardButton('Ochirish', callback_data='delete-' + str(id))
        ],
        [
            InlineKeyboardButton('Ortga', callback_data='back')
        ]
    ]


def back_button():
    return [
        [
            InlineKeyboardButton('◀️ Ortga', callback_data='back-menu')
        ],
    ]


def login(update, context):
    print('login')
    try:
        if update.callback_query is not None:
            query = update.callback_query
            data = query.data
            if data == 'back-menu':
                query.message.edit_text('🟢 Bekor qilindi\n👉🏽  /start')
                query.answer()
                return STATE_MAIN
        else:
            if update.message.text is not None:
                db = DBHelper()
                password = update.message.text.split('-')
                if password[0] == PASSWORD_ADMIN:
                    delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id - 1)
                    update.message.delete()
                    update.message.reply_html(text='🏠 Menu',
                                              reply_markup=ReplyKeyboardMarkup(admin_buttons(), resize_keyboard=True,
                                                                               one_time_keyboard=True))
                    return STATE_ADMIN

            update.message.reply_html('❗️ Admin paroli noto\'g\'ri kiritildi\n Qayta kiriting:',
                                      reply_markup=InlineKeyboardMarkup(back_button()))
            return STATE_LOGIN
    except Exception as e:
        print(traceback.format_exc())


def admin_menu(update, context):
    print('admin_menu')
    try:
        if update.message is not None:
            db = DBHelper()
            if update.message.text is not None:
                if update.message.text == BTN_CREATE:
                    update.message.reply_html('Chat Yaratish',
                                              reply_markup=InlineKeyboardMarkup(create_btns(attributes, {})))
                    return STATE_ADD
                if update.message.text == BTN_CHANGE:
                    update.message.reply_html('Mavjud chatlar',
                                              reply_markup=InlineKeyboardMarkup(chat_btns(db.get_chats())))
                    return STATE_CHOOSE

            update.message.reply_html(text='🏠 Menu',
                                      reply_markup=ReplyKeyboardMarkup(admin_buttons(), resize_keyboard=True,
                                                                       one_time_keyboard=True))
            return STATE_ADMIN

    except Exception as e:
        print(traceback.format_exc())


def add_chat(update, context):
    try:
        if update.callback_query is not None:
            query = update.callback_query
            data = query.data
            # print(data)
            # print('context', context.user_data)

            if data == 'cancel':
                query.message.delete()
                query.answer('Bekor Qilindi.', show_alert=True)
                context.user_data.clear()
                query.message.reply_html(text='🏠 Menu',
                                         reply_markup=ReplyKeyboardMarkup(admin_buttons(), resize_keyboard=True,
                                                                          one_time_keyboard=True))
                return STATE_ADMIN
            if data == 'save':
                query.answer()
                db = DBHelper()
                if context.user_data.get('attribute') is not None:
                    del context.user_data['attribute']

                db.insert('chats', context.user_data)

                context.bot.sendMessage(context.user_data.get('freelancer_id'), text="Sizni chatga taklif qilishdi!",
                                        reply_markup=InlineKeyboardMarkup(begin_conservation_btn('freelancer')))
                context.bot.sendMessage(context.user_data.get('client_id'), text="Sizni chatga taklif qilishdi!",
                                        reply_markup=InlineKeyboardMarkup(begin_conservation_btn('client')))

                query.message.reply_html('Saqlandi')
                context.user_data.clear()

                query.message.reply_html(text='🏠 Menu',
                                         reply_markup=ReplyKeyboardMarkup(admin_buttons(), resize_keyboard=True,
                                                                          one_time_keyboard=True))
                return STATE_ADMIN
            elif data == 'is_admin':
                context.user_data['is_admin'] = 1
                query.answer('Botni admin qiling!', show_alert=True)
                query.message.edit_text('Chat Yaratish',
                                        reply_markup=InlineKeyboardMarkup(create_btns(attributes, context.user_data)))
            else:
                context.user_data['attribute'] = data
                context.user_data[data] = data
                query.answer()
                query.message.reply_html(attributes.get(data) + " ni kiriting")

        elif update.message is not None:
            if context.user_data.get('attribute') is not None:
                context.user_data[context.user_data['attribute']] = update.message.text
                update.message.reply_html('Chat Yaratish',
                                          reply_markup=InlineKeyboardMarkup(create_btns(attributes, context.user_data)))

    except Exception as e:
        print(traceback.format_exc())


def change_chat(update, context):
    try:
        db = DBHelper()

        if update.callback_query is not None:
            query = update.callback_query
            data = query.data
            # print(data)
            # print('context', context.user_data)

            if data == 'back':
                query.answer()
                query.message.edit_text('Mavjud chatlar',
                                        reply_markup=InlineKeyboardMarkup(chat_btns(db.get_chats())))
                return STATE_CHOOSE
            else:
                split = data.split('-')

                if split[0] == 'change':
                    query.message.reply_html("Yangi Frilancer Id sini kiriting")
                    context.user_data['attribute'] = 'freelancer_id'
                    context.user_data['id'] = split[1]
                elif split[0] == 'delete':
                    query.message.delete()
                    query.answer('Bajarildi!', show_alert=True)
                    db.update('chats', split[1], {'status': 2})
                    query.message.edit_text('Mavjud chatlar',
                                            reply_markup=InlineKeyboardMarkup(chat_btns(db.get_chats())))
                    return STATE_CHOOSE
        elif update.message is not None:
            update.message.delete()
            if context.user_data.get('attribute') == 'freelancer_id':
                db.update('chats', context.user_data['id'], {'freelancer_id': update.message.text})
                update.message.reply_html('Bajarildi!')
                chat = db.get_chat(context.user_data['id'])
                context.bot.sendMessage(update.message.text, text="Sizni chatga taklif qilishdi!",
                                        reply_markup=InlineKeyboardMarkup(begin_conservation_btn()))
                context.bot.sendMessage(chat['client_id'], text="Sizni chatga taklif qilishdi!",
                                        reply_markup=InlineKeyboardMarkup(begin_conservation_btn()))
                # print(chat)

                message = "Nomi: {}\nFrilanser ID: {}\nZakazchik ID: {}\nKanal Linki: {}".format(chat['name'],
                                                                                                 chat['freelancer_id'],
                                                                                                 chat['client_id'],
                                                                                                 chat['channel_link'])
                context.user_data.clear()
                update.message.reply_html(
                    message,
                    reply_markup=InlineKeyboardMarkup(chat_setting_btns(chat['id']))
                )
    except Exception as e:
        print(traceback.format_exc())


def choose_chat(update, context):
    try:
        if update.callback_query is not None:
            query = update.callback_query
            data = query.data
            # print(data)
            # print('context', context.user_data)

            if data == 'cancel':
                query.answer()
                query.message.reply_html(text='🏠 Menu',
                                         reply_markup=ReplyKeyboardMarkup(admin_buttons(), resize_keyboard=True,
                                                                          one_time_keyboard=True))
                return STATE_ADMIN
            db = DBHelper()
            chat = db.get_chat(data)

            # print(chat)

            message = "Nomi: {}\nFrilanser ID: {}\nZakazchik ID: {}\nKanal Linki: {}".format(chat['name'],
                                                                                             chat['freelancer_id'],
                                                                                             chat['client_id'],
                                                                                             chat['channel_link'])
            query.answer()

            query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(chat_setting_btns(chat['id']))
            )
            return STATE_SETTINGS
        elif update.message is not None:
            update.message.delete()

    except Exception as e:
        print(traceback.format_exc())


def delete_message(chat_id, message_id):
    try:
        url = "https://api.telegram.org/bot" + TOKEN + "/deleteMessage"
        response = requests.post(url, data={'chat_id': chat_id, 'message_id': message_id})
        # print('response', response.json())
        if response.status_code == requests.codes.ok:
            return response.json()
        return False
    except Exception as e:
        print(traceback.format_exc())


def send_message(chat_id, text, reply_markup=None):
    try:
        url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
        response = requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML',
                                            'reply_markup': reply_markup})
        # print('response', response.json())
        if response.status_code == requests.codes.ok:
            return response.json()['result']['message_id']
        return False
    except Exception as e:
        print(traceback.format_exc())


def admin(update, context):
    print('admin')
    try:
        if update.callback_query is not None:
            pass
        else:
            update.message.reply_html('🔐 Parolni kiriting:')
            return STATE_LOGIN
    except Exception as e:
        print(traceback.format_exc())
