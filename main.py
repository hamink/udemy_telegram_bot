from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext, CallbackQueryHandler)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.utils.helpers import create_deep_linked_url
from data_source import DataSource
import os
import logging
import sys
import requests

GET_LINK_TEXT = 'Get Link'
CHECK_BALANCE = "Check my balance"
CHECK_LEADERBOARD = 'Check LEADERBOARD 🏆'

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
else:
    logger.error("No mode specified!")
    sys.exit(1)

def start_handler(update: Update, context: CallbackContext):
    if not context.args:
        dataSource.add_new_user(update.message.from_user.id, update.message.from_user.username, 0, 0)
    else:
        param_value = context.args[0]
        validParam = dataSource.check_valid_param(update.message.from_user.username, param_value)
        if validParam:
            dataSource.add_new_user(update.message.from_user.id, update.message.from_user.username, 20, 0)
            dataSource.update_balance(param_value)
        else:
            dataSource.add_new_user(update.message.from_user.id, update.message.from_user.username, 0, 0)

    update.message.reply_text("Hello, Welcome to the Leedo project! \n\nPlease join our group and click continue \n\n", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Join group', url='https://t.me/leedo_project')],
    [InlineKeyboardButton('Continue', callback_data='join_competition')],
    ]))

def join_competition(update: Update, context: CallbackContext):
    try:
        response = requests.get("https://api.telegram.org/bot%s/getChatMember?chat_id=-1001617803218&user_id=%s" % (TOKEN, update.callback_query.message.from_user.id))
        if response.ok == False:
            update.callback_query.message.reply_text("Join Leedo group first and click continue - https://t.me/leedo_project")
        else:
            update.callback_query.message.reply_text("You are now participated to the competition! Check out buttons below", reply_markup=add_buttons())
    except requests.ConnectionError as error:
        print(error)

def add_buttons():
    keyboard = [[KeyboardButton(GET_LINK_TEXT), KeyboardButton(CHECK_BALANCE)],
                [KeyboardButton(CHECK_LEADERBOARD)],
                ]
    return ReplyKeyboardMarkup(keyboard)

def generate_handler(update: Update, context: CallbackContext):
    url = create_deep_linked_url(context.bot.get_me().username, update.message.chat.username)
    update.message.reply_text(text="Share it with your friends: %s\nCopy the link and share it with them" % url)

def check_balance(update: Update, context: CallbackContext):
    current_balance = dataSource.get_balance(update.message.from_user.username)
    update.message.reply_text("This is your balance: {} \nThis is your referral number: {}".format(current_balance[0], current_balance[1]))

def check_leaderboard(update: Update, context: CallbackContext):
    ranking = dataSource.get_ranking()
    update.message.reply_text(text="*rank: id - balance*", parse_mode=ParseMode.MARKDOWN)
    number = 1
    for rank in ranking:
        update.message.reply_text("{}: {} - {}".format(number, rank[0], rank[1]))
        number += 1

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(join_competition))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(GET_LINK_TEXT), generate_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(CHECK_BALANCE), check_balance))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(CHECK_LEADERBOARD), check_leaderboard))
    dataSource.create_tables()
    run()
