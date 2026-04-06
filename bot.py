import os
import random
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

WELCOME = "🌙 أهلاً بك في بوت القرآن الكريم"

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء"]
READERS = [
    ("العفاسي","https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/")
]

MAIN = ReplyKeyboardMarkup([
    ["📖 اختر سورة","🎲 سورة عشوائية"],
    ["🔍 بحث"]
], resize_keyboard=True)

# -------- start --------
def start(update, context):
    update.message.reply_text(WELCOME, reply_markup=MAIN)

# -------- buttons --------
def buttons(update, context):
    text = update.message.text

    if text == "📖 اختر سورة":
        keyboard = [[InlineKeyboardButton(s, callback_data=f"s_{i+1}")] for i,s in enumerate(SURAHS)]
        update.message.reply_text("اختر:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🎲 سورة عشوائية":
        i = random.randint(1,len(SURAHS))
        context.user_data["s"] = i
        keyboard = [[InlineKeyboardButton("العفاسي", callback_data="r_0")]]
        update.message.reply_text(SURAHS[i-1], reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🔍 بحث":
        context.user_data["search"] = True
        update.message.reply_text("اكتب اسم السورة")

    elif context.user_data.get("search"):
        context.user_data["search"] = False
        keyboard = [[InlineKeyboardButton(s, callback_data=f"s_{i+1}")] for i,s in enumerate(SURAHS)]
        update.message.reply_text("النتائج:", reply_markup=InlineKeyboardMarkup(keyboard))

# -------- callback --------
def callback(update, context):
    q = update.callback_query
    q.answer()
    data = q.data

    if data.startswith("s_"):
        i = int(data.split("_")[1])
        context.user_data["s"] = i
        keyboard = [[InlineKeyboardButton("العفاسي", callback_data="r_0")]]
        q.edit_message_text(SURAHS[i-1], reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("r_"):
        surah = context.user_data.get("s",1)
        url = READERS[0][1] + str(surah).zfill(3) + ".mp3"
        q.message.reply_audio(url)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text, buttons))
dispatcher.add_handler(CallbackQueryHandler(callback))

# -------- webhook --------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    app.run()
