from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext, CallbackQueryHandler)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.utils.helpers import create_deep_linked_url
from data_source import DataSource
import os
import logging
import sys
import requests

GET_LINK_TEXT = '레퍼럴 링크 받기'
CHECK_BALANCE = "내 밸런스 체크"
CHECK_LEADERBOARD = '총 순위 체크 🏆'

MODE = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
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

# start handler uses param to update the user who shared their referral link
def start_handler(update: Update, context: CallbackContext):
    global param
    if not context.args:
        param = 'noParam'
    else:
        param = context.args
    update.message.reply_text("이도 프로젝트에 오신것을 환영합니다! \n\n이도 그룹에 참여하시고 '계속하기'를 클릭해주세요. \n\n", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton(text='이도 그룹 참여하기', url='https://t.me/leedo_project')],
    [InlineKeyboardButton('계속하기', callback_data='join_competition')],
    ]))

# join competition determines whether the user joined Leedo project group. If the user already joined, this funtion confirms if whether the param is valid.
def join_competition(update: Update, context: CallbackContext):
    try:
        response = requests.get("https://api.telegram.org/bot%s/getChatMember?chat_id=-1001617803218&user_id=%s" % (TOKEN, update.callback_query.message.from_user.id))
        if response.ok == False:
            update.callback_query.message.reply_text("이도 그룹에 가입하시고 '계속하기'를 클릭해주세요 - https://t.me/leedo_project")
        else:
            update.callback_query.message.reply_text("레퍼럴 경쟁 게임에 오신 것을 환영합니다! 밑의 버튼들을 클릭해보세요 👇", reply_markup=add_buttons())
            if param == 'noParam':
                dataSource.add_new_user(update.callback_query.message.chat.id, update.callback_query.message.chat.username, 0, 0)
            else:
                validParam = dataSource.check_valid_param(update.callback_query.message.chat.username, param[0])
                if validParam:
                    dataSource.add_new_user(update.callback_query.message.chat.id, update.callback_query.message.chat.username, 10, 0)
                    dataSource.update_balance(param[0])
                else:
                    dataSource.add_new_user(update.callback_query.message.chat.id, update.callback_query.message.chat.username, 0, 0)
    except requests.ConnectionError as error:
        print(error)

def add_buttons():
    keyboard = [[KeyboardButton(GET_LINK_TEXT), KeyboardButton(CHECK_BALANCE)],
                [KeyboardButton(CHECK_LEADERBOARD)],
                ]
    return ReplyKeyboardMarkup(keyboard)

# generate hanlder gives a user referral link 
def generate_handler(update: Update, context: CallbackContext):
    url = create_deep_linked_url(context.bot.get_me().username, update.message.chat.username)
    update.message.reply_text(text="이도 프로젝트와 뜻을 같이 할 사람들에게 공유해주세요: %s\n 윗 링크를 공유하시고 레퍼럴 컴페티션에서 우승하세요. 우승 상품도 있습니다!" % url)

# check balance shows the current balance
def check_balance(update: Update, context: CallbackContext):
    current_balance = dataSource.get_balance(update.message.from_user.username)
    update.message.reply_text("내 밸런스: {} \n레퍼럴 숫자: {}".format(current_balance[0], current_balance[1]))

# check leaderboard shows the current leaderboard
def check_leaderboard(update: Update, context: CallbackContext):
    ranking = dataSource.get_ranking()
    update.message.reply_text(text="*랭킹: 아이디 - 밸런스", parse_mode=ParseMode.MARKDOWN)
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
