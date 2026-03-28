import os
import json
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# قائمة السور
SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

# قائمة القراء
READERS_LIST = [
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط", "https://server7.mp3quran.net/basit/"),
    ("السديس", "https://server11.mp3quran.net/sds/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/")
]

# دالة لإنشاء أزرار القراء (3 في كل سطر)
def get_readers_kb():
    keyboard = []
    for i in range(0, len(READERS_LIST), 3):
        row = [InlineKeyboardButton(READERS_LIST[j][0], callback_data=f"r_{j}") for j in range(i, min(i + 3, len(READERS_LIST)))]
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# دالة لإنشاء أزرار السور
def get_surah_kb(page=1):
    start, end = (1, 58) if page == 1 else (58, 115)
    keyboard = []
    for i in range(start, end, 3):
        row = [InlineKeyboardButton(f"{j}. {SURAHS[j-1]}", callback_data=f"s_{j}") for j in range(i, min(i + 3, end))]
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("التالي ◀️" if page==1 else "▶️ السابق", callback_data=f"p_{2 if page==1 else 1}")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([["📖 اختر سورة", "🎲 سورة عشوائية"], ["🔍 بحث عن سورة", "⭐ قارئي المفضل"]], resize_keyboard=True)
    await update.message.reply_text("✨ مرحباً بك في بوت القرآن الكريم\nاختر سورة للبدء:", reply_markup=kb)
    await update.message.reply_text("📖 قائمة السور:", reply_markup=get_surah_kb(1))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📖 اختر سورة":
        await update.message.reply_text("📖 اختر السورة:", reply_markup=get_surah_kb(1))
    elif text == "🎲 سورة عشوائية":
        n = random.randint(1, 114)
        context.user_data["s"] = str(n)
        await update.message.reply_text(f"🎲 سورة {SURAHS[n-1]}\n🎙️ اختر القارئ:", reply_markup=get_readers_kb())
    elif text == "⭐ قارئي المفضل":
        fav = context.user_data.get("fav_reader")
        if fav is not None:
            await update.message.reply_text(f"⭐ قارئك المفضل: {READERS_LIST[fav][0]}\n📖 اختر السورة الآن:", reply_markup=get_surah_kb(1))
        else:
            await update.message.reply_text("❌ لم تختر قارئاً بعد. اختر سورة ثم قارئ وسيتم حفظه تلقائياً.")
    elif text == "🔍 بحث عن سورة":
        context.user_data["searching"] = True
        await update.message.reply_text("🔍 اكتب اسم السورة:")
