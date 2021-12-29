from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler,
                          Filters, CallbackContext, CallbackQueryHandler)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.utils.helpers import create_deep_linked_url
from data_source import DataSource
import os
import threading
import time
import datetime
import logging
import sys
import requests

GET_LINK_TEXT = 'Get Link'
CHECK_BALANCE = "Check my balance"
CHECK_LEADERBOARD = 'Check LEADERBOARD 🏆'
INTERVAL = 30

MODE = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
ENTER_MESSAGE, ENTER_TIME = range(2)
dataSource = DataSource(os.environ.get("DATABASE_URL"))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if MODE == "dev":
    def run():
        logger.info("Start in DEV mode")
        updater.start_polling()
elif MODE == "prod":
    def run():
        logger.info("Start in PROD mode")
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", "8443")), url_path=TOKEN,
                              webhook_url="https://{}.herokuapp.com/{}".format(os.environ.get("APP_NAME"), TOKEN))
        print("test", updater.bot.get_webhook_info())
else:
    logger.error("No mode specified!")
    sys.exit(1)


def start_handler(update, context):
    if not context.args:
        param_value = ''
        print("it is empty param")
        print(update.message)
    else:
        param_value = context.args[0]
        print("it is not empty param")

    print(param_value)
    update.message.reply_text("Hello, Welcome to the Leedo project! \n\nPlease join our group and click continue \n\n", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Join group', url='https://t.me/realtest11')],
        [InlineKeyboardButton('Continue', callback_data='join_competition')],
    ]))

def join_competition(update, context):
    # result = Bot.get_chat_member(chat_id=-1001530425621, user_id=update.callback_query.message.from_user.id)
    # print(result)
    try:
        response = requests.get("https://api.telegram.org/bot%s/getChatMember?chat_id=-1001530425621&user_id=%s" % (TOKEN, update.callback_query.message.from_user.id))
        if response.ok == False:
            update.callback_query.message.reply_text("Join Leedo group first and click continue")
        else:
            update.callback_query.message.reply_text("Well done", reply_markup=add_buttons())
    except requests.ConnectionError as error:
        print(error)
     # print("get")
    # show_list = []
    # show_list.append(InlineKeyboardButton("on", callback_data="on")) # add on button
    # show_list.append(InlineKeyboardButton("off", callback_data="off")) # add off button
    # show_list.append(InlineKeyboardButton("cancel", callback_data="cancel")) # add cancel button
    # show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list) - 1)) # make markup

    # update.message.reply_text("Hello, master!", reply_markup=InlineKeyboardMarkup([
    #     # [InlineKeyboardButton(text='on Facebook', url='https://facebook.com', callback_data='telegram')],
    #     # [InlineKeyboardButton(text='on Telegram', callback_data=str(telegram()))],
    #     [InlineKeyboardButton("on", callback_data="on")],
    #     [InlineKeyboardButton("off", callback_data="off")],
    #     [InlineKeyboardButton("cancel", callback_data="cancel")],
    # ]))

    # query = update.callback_query

    # keyboard = [[InlineKeyboardButton('rules', url = 'https://google.com')]]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text(
    #                         text = "I'm a bot, please talk to me!",
    #                          reply_markup = reply_markup)
    # print(update.callback_query)
def add_buttons():
    keyboard = [[KeyboardButton(GET_LINK_TEXT), KeyboardButton(CHECK_BALANCE)],
                [KeyboardButton(CHECK_LEADERBOARD)],
                ]
    return ReplyKeyboardMarkup(keyboard)

# def button (update, context):
#     print("test5", update.callback_context)
#     update.callback_query.data
#     query = update.callback_context
#     query.answer()

# def callback_get(update, context):
#     print("callback")
#     context.bot.edit_message_text(text="{}이(가) 선택되었습니다".format(update.callback_query.data),
#                                   chat_id=update.callback_query.message.chat_id,
#                                   message_id=update.callback_query.message.message_id,)
    
    
# def join_handler(update, context):
#     update.message.replay_text("")

# def telegram():
#     print("test2")

# def add_reminder_button():
#     keyboard = [[KeyboardButton(ADD_REMINDER_TEXT)],
#                 [KeyboardButton(ADD_REMINDER_TEXT), InlineKeyboardButton(text='on Facebook', url='https://facebook.com')],
#                 ]
#     # keyboard = InlineKeyboardMarkup([
#     #     [InlineKeyboardButton(text='on Facebook', callback_data='Facebook')],
#     #     [InlineKeyboardButton(text='on Telegram', callback_data='Telegram')],
#     # ])
#     return ReplyKeyboardMarkup(keyboard)

# def remove_reminder_button():
#     keyboard = []
#     return ReplyKeyboardMarkup(keyboard)


# def add_reminder_handler(update: Update, context: CallbackContext):
#     update.message.reply_text("Please enter a message of the reminder:")
#     return ENTER_MESSAGE


# def enter_message_handler(update: Update, context: CallbackContext):
#     update.message.reply_text("Please enter a time when bot should remind:")
#     context.user_data["message_text"] = update.message.text
#     return ENTER_TIME


# def enter_time_handler(update: Update, context: CallbackContext):
#     message_text = context.user_data["message_text"]
#     time = datetime.datetime.strptime(update.message.text, "%d/%m/%Y %H:%M")
#     message_data = dataSource.create_reminder(update.message.chat_id, message_text, time)
#     update.message.reply_text("Your reminder: " + message_data.__repr__())
#     return ConversationHandler.END


# def start_check_reminders_task():
#     thread = threading.Thread(target=check_reminders, args=())
#     thread.daemon = True
#     thread.start()


# def check_reminders():
#     while True:
#         for reminder_data in dataSource.get_all_reminders():
#             if reminder_data.should_be_fired():
#                 dataSource.fire_reminder(reminder_data.reminder_id)
#                 updater.bot.send_message(reminder_data.chat_id, reminder_data.message)
#         time.sleep(INTERVAL)

def generate_handler(update: Update, context: CallbackContext):
    url = create_deep_linked_url(context.bot.get_me().username, update.message.chat.username)
    update.message.reply_text(text="Share it with your friends: %s\n Copy the link and share it with them" % url)

def check_balance(update: Update, context: CallbackContext):
    update.message.reply_text("This is your balance:")

def check_leaderboard(update: Update, context: CallbackContext):
    update.message.reply_text("Check your rank:")

# def new_member(update: Update, context: CallbackContext):
#     print(update.message)
#     update.message.reply_text(update.message.new_chat_members)

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    # conv_handler = ConversationHandler(
    #     entry_points=[MessageHandler(Filters.regex(GET_LINK_TEXT), add_reminder_handler)],
    #     states={
    #         ENTER_MESSAGE: [MessageHandler(Filters.all, enter_message_handler)],
    #         ENTER_TIME: [MessageHandler(Filters.all, enter_time_handler)]
    #     },
    #     fallbacks=[]
    # )
    # updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(join_competition))
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(GET_LINK_TEXT), generate_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(CHECK_BALANCE), check_balance))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(CHECK_LEADERBOARD), check_leaderboard))
    # updater.dispatcher.add_handler(MessageHandler(Filters.all, new_member))
    dataSource.create_tables()
    run()
    # start_check_reminders_task()

