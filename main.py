# base requirements
import traceback

# telergam methods
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler)

from admin import (
    login,
    admin,
    admin_menu,
    add_chat,
    choose_chat,
    change_chat,
)
# confuguration
from config import (
    TOKEN,
    STATE_MAIN,
    STATE_ADMIN,
    STATE_CHOOSE,
    STATE_SETTINGS,
    STATE_ADD,
    STATE_LOGIN,
)
# get db connect functions
from db_helper import DBHelper


def start(update, context):
    print('start')
    try:
        db = DBHelper()
        if update.callback_query is not None:
            query = update.callback_query
            data = query.data.split('-')
            # telegramid = update.callback_query.message.chat.id
            # user = db.get_user(telegramid)
            if data[0] == 'begin':
                query.answer()
                # print(data)
                user = ''
                if data[1] == 'client':
                    user = 'Client'
                elif data[1] == 'freelancer':
                    user = 'Freelancer'

                query.message.edit_text('Admin:\n' + 'Sizni vazifangiz ' + user)
                return STATE_MAIN
        else:
            telegramid = update.message.chat.id
            first_name = update.message.chat.first_name
            user = db.get_user(telegramid)

            # print('user', user)
            if not user:
                db.user_save({'telegramid': telegramid, 'first_name': first_name})

            chat = db.get_partner(telegramid)

            # print('chat', chat)

            if update.message.text is not None and update.message.text == '/start':
                update.message.reply_html("Assalomu alaykum {}!".format(first_name))
            else:
                if not chat:
                    update.message.reply_html("Uzr hali chat yaratilmagan. Admin bilan bog'laning!")
                else:
                    context.bot.copyMessage(chat.get('id'), telegramid, update.message.message_id)
                    context.bot.forwardMessage(chat.get('link'), telegramid, update.message.message_id)

        return STATE_MAIN
    except Exception as e:
        print(traceback.format_exc())


def main():
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(start), MessageHandler(Filters.all, start)],
        states={
            STATE_MAIN: [CommandHandler('start', start), MessageHandler(Filters.all, start)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # admin menu
    admin_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin)],
        states={
            STATE_LOGIN: [MessageHandler(Filters.all, login), CallbackQueryHandler(login)],
            STATE_ADMIN: [CallbackQueryHandler(admin_menu), MessageHandler(Filters.all, admin_menu)],
            STATE_ADD: [CallbackQueryHandler(add_chat), MessageHandler(Filters.all, add_chat)],
            STATE_CHOOSE: [CallbackQueryHandler(choose_chat), MessageHandler(Filters.all, choose_chat)],
            STATE_SETTINGS: [CallbackQueryHandler(change_chat), MessageHandler(Filters.all, change_chat)],
        },
        fallbacks=[CommandHandler('admin', admin)],
    )

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(admin_conversation_handler)
    dispatcher.add_handler(conversation_handler)
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == '__main__':
    main()
