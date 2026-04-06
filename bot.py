import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

WELCOME_MESSAGE = """🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲"""

READERS = [
    ("مشاري العفاسي","https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/"),
    ("ماهر المعيقلي","https://server12.mp3quran.net/maher/"),
    ("خالد الجليل","https://server10.mp3quran.net/jleel/")
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس"]

MAIN = ReplyKeyboardMarkup([
    ["📖 اختر سورة","🎲 سورة عشوائية"],
    ["🔍 بحث"]
], resize_keyboard=True)

# ----------- start -----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN)

# ----------- buttons -----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📖 اختر سورة":
        keyboard = [[InlineKeyboardButton(s, callback_data=f"s_{i+1}")] for i,s in enumerate(SURAHS)]
        await update.message.reply_text("اختر:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🎲 سورة عشوائية":
        i = random.randint(1,len(SURAHS))
        context.user_data["s"] = i
        keyboard = [[InlineKeyboardButton(r[0], callback_data=f"r_{idx}")] for idx,r in enumerate(READERS)]
        await update.message.reply_text(SURAHS[i-1], reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🔍 بحث":
        context.user_data["search"] = True
        await update.message.reply_text("اكتب اسم السورة")

    elif context.user_data.get("search"):
        context.user_data["search"] = False
        res = [(i,s) for i,s in enumerate(SURAHS) if text in s]
        if not res:
            await update.message.reply_text("❌ لا يوجد")
            return
        keyboard = [[InlineKeyboardButton(s, callback_data=f"s_{i+1}")] for i,s in res]
        await update.message.reply_text("النتائج:", reply_markup=InlineKeyboardMarkup(keyboard))

# ----------- callback -----------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("s_"):
        i = int(data.split("_")[1])
        context.user_data["s"] = i
        keyboard = [[InlineKeyboardButton(r[0], callback_data=f"r_{idx}")] for idx,r in enumerate(READERS)]
        await q.edit_message_text(SURAHS[i-1], reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("r_"):
        idx = int(data.split("_")[1])
        surah = context.user_data.get("s",1)
        url = READERS[idx][1] + str(surah).zfill(3) + ".mp3"

        await q.message.reply_audio(url, caption=SURAHS[surah-1])

# ----------- run -----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, buttons))
app.add_handler(CallbackQueryHandler(callback))

app.run_polling()
