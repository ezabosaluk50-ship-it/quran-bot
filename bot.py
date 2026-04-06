import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

USERS_FILE = "users.json"

WELCOME_MESSAGE = """🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲"""

READERS_LIST = [
    ("مشاري العفاسي","https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/"),
    ("ماهر المعيقلي","https://server12.mp3quran.net/maher/"),
    ("عبد الباسط","https://server7.mp3quran.net/basit/"),
    ("ناصر القطامي","https://download.quranicaudio.com/quran/naasir_al-qataami/"),
    ("سعد الغامدي","https://server7.mp3quran.net/s_gmd/"),
    ("السديس","https://server11.mp3quran.net/sds/"),
    ("المنشاوي","https://download.quranicaudio.com/quran/muhammad_siddeeq_al-minshaawee/"),
    ("إدريس أبكر","https://download.quranicaudio.com/quran/idrees_abkar/"),
    ("ياسر الدوسري","https://download.quranicaudio.com/quran/yasser_ad-dussary/"),
    ("خالد الجليل","https://server10.mp3quran.net/jleel/"),
    ("أحمد العجمي","https://server10.mp3quran.net/ajm/"),
    ("الحصري","https://download.quranicaudio.com/quran/mahmood_khaleel_al-husaree/"),
    ("علي الحذيفي","https://server9.mp3quran.net/hthfi/"),
    ("هاني الرفاعي","https://server8.mp3quran.net/hani/"),
    ("فارس عباد","https://server8.mp3quran.net/frs_a/"),
    ("عبدالله الجهني","https://download.quranicaudio.com/quran/abdullaah_3awwaad_al-juhaynee/"),
    ("إسلام صبحي","https://server8.mp3quran.net/islam/")
]

SURAHS = [ ... نفس القائمة تبعك بدون تغيير ... ]

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/start")],
        [KeyboardButton("📖 اختر سورة"), KeyboardButton("🎲 سورة عشوائية")],
        [KeyboardButton("🔍 بحث عن سورة"), KeyboardButton("⭐ قارئي المفضل")]
    ],
    resize_keyboard=True
)

# -------- إرسال الصوت (سريع) --------
async def send_audio(context, chat_id, url, caption):
    try:
        await context.bot.send_audio(chat_id=chat_id, audio=url, caption=caption)
    except:
        await context.bot.send_message(chat_id, "❌ حدث خطأ في إرسال السورة")

# -------- الأزرار النصية --------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎲 سورة عشوائية":
        num = random.randint(1, 114)
        context.user_data["surah"] = num
        await update.message.reply_text(
            f"🎲 سورة {SURAHS[num-1]}",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard())
        )

    elif text == "📖 اختر سورة":
        await update.message.reply_text(
            "📖 اختر السورة:",
            reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1))
        )

    elif text == "🔍 بحث عن سورة":
        context.user_data["search"] = True
        await update.message.reply_text("🔍 اكتب اسم السورة")

    elif text == "⭐ قارئي المفضل":
        fav = context.user_data.get("fav")
        if fav is not None:
            await update.message.reply_text(f"⭐ قارئك: {READERS_LIST[fav][0]}")
        else:
            await update.message.reply_text("❌ لا يوجد قارئ مفضل")

    elif context.user_data.get("search"):
        context.user_data["search"] = False
        results = [(i+1, s) for i,s in enumerate(SURAHS) if text in s]

        if not results:
            await update.message.reply_text("❌ لم يتم العثور")
            return

        keyboard = []
        for num, name in results:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"surah_{num}")])

        await update.message.reply_text("📖 النتائج:", reply_markup=InlineKeyboardMarkup(keyboard))

# -------- واجهات --------
def build_surah_keyboard(page=1):
    data = SURAHS[:57] if page == 1 else SURAHS[57:]
    keyboard, row = [], []

    for i, name in enumerate(data):
        idx = i+1 if page == 1 else i+58
        row.append(InlineKeyboardButton(name, callback_data=f"surah_{idx}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("التالي", callback_data="page_2" if page == 1 else "page_1"),
        InlineKeyboardButton("🎲", callback_data="random")
    ])

    return keyboard

def build_readers_keyboard():
    keyboard = []
    for i,(name,_) in enumerate(READERS_LIST):
        keyboard.append([InlineKeyboardButton(name, callback_data=f"reader_{i}")])
    return keyboard

# -------- start --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN_KEYBOARD)

# -------- callback --------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("page"):
        page = 1 if "1" in data else 2
        await q.edit_message_text("📖 اختر:", reply_markup=InlineKeyboardMarkup(build_surah_keyboard(page)))

    elif data == "random":
        num = random.randint(1,114)
        context.user_data["surah"] = num
        await q.edit_message_text(SURAHS[num-1], reply_markup=InlineKeyboardMarkup(build_readers_keyboard()))

    elif data.startswith("surah"):
        num = int(data.split("_")[1])
        context.user_data["surah"] = num
        await q.edit_message_text(
            f"{SURAHS[num-1]}",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard())
        )

    elif data.startswith("reader"):
        i = int(data.split("_")[1])
        context.user_data["fav"] = i

        surah = context.user_data.get("surah",1)
        url = READERS_LIST[i][1] + str(surah).zfill(3) + ".mp3"

        # زر مشاركة
        keyboard = [[
            InlineKeyboardButton("📤 مشاركة السورة", switch_inline_query=url)
        ]]

        await send_audio(context, q.message.chat_id, url, SURAHS[surah-1])
        await q.message.reply_text("⬆️ مشاركة السورة:", reply_markup=InlineKeyboardMarkup(keyboard))

# -------- تشغيل --------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_polling()
