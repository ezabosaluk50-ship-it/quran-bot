import os
import random
import logging
import requests
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# 1. القائمة الكاملة (14 قارئاً) مع روابط دقيقة
READERS_LIST = [
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط عبد الصمد", "https://server7.mp3quran.net/basit/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("عبدالرحمن السديس", "https://server11.mp3quran.net/sds/"),
    ("محمد المنشاوي", "https://server10.mp3quran.net/minsh/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/"),
    ("محمود الحصري", "https://server13.mp3quran.net/husr/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

# --- لوحة المفاتيح ---
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("ابدأ 🤍"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("🎲 سورة عشوائية"), KeyboardButton("🔍 بحث")]
    ], resize_keyboard=True)

def build_surah_keyboard(page=1):
    start, end = (0, 57) if page == 1 else (57, 114)
    keyboard = []
    row = []
    for i in range(start, end):
        row.append(InlineKeyboardButton(f"{i+1}. {SURAHS[i]}", callback_data=f"surah_{i+1}"))
        if len(row) == 3:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    nav = [InlineKeyboardButton("التالي ◀️", callback_data="page_2")] if page == 1 else [InlineKeyboardButton("▶️ السابق", callback_data="page_1")]
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def build_readers_keyboard():
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"reader_{i}"))
        if len(row) == 2:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# --- الوظيفة الأساسية لإرسال الصوت مع "محاولة ثانية" ---
async def send_quran_audio(context, chat_id, r_name, r_url, s_num, status_msg):
    # قائمة بالسيرفرات البديلة (أحياناً يشتغل server11 بدلاً من server10)
    servers_to_try = [r_url, r_url.replace("server10", "server11"), r_url.replace("server10", "server6")]
    
    for url in servers_to_try:
        file_url = f"{url}{str(s_num).zfill(3)}.mp3"
        try:
            response = requests.get(file_url, timeout=15, stream=True)
            if response.status_code == 200:
                audio_content = BytesIO(response.content)
                audio_content.name = f"{SURAHS[s_num-1]}.mp3"
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_content,
                    title=f"سورة {SURAHS[s_num-1]}",
                    performer=r_name
                )
                await status_msg.delete()
                return True
        except:
            continue
    return False

# --- معالجة الضغطات ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("page_"):
        await query.edit_message_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(int(query.data.split("_")[1])))
    elif query.data.startswith("surah_"):
        context.user_data["s_num"] = int(query.data.split("_")[1])
        await query.edit_message_text(f"🎙 اختر القارئ لسورة {SURAHS[context.user_data['s_num']-1]}:", reply_markup=build_readers_keyboard())
    elif query.data.startswith("reader_"):
        idx = int(query.data.split("_")[1])
        s_num = context.user_data.get("s_num", 1)
        r_name, r_url = READERS_LIST[idx]
        
        msg = await query.edit_message_text(f"⏳ جاري تجهيز سورة {SURAHS[s_num-1]} بصوت {r_name}...")
        
        success = await send_quran_audio(context, query.message.chat_id, r_name, r_url, s_num, msg)
        if not success:
            await msg.edit_text(f"❌ عذراً، سورة {SURAHS[s_num-1]} غير متوفرة حالياً بصوت {r_name}. حاول مع قارئ آخر.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌙 أهلاً بك في بوت القرآن الكريم 🌙", reply_markup=get_main_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "ابدأ" in text: await start(update, context)
    elif "اختر سورة" in text: await update.message.reply_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(1))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
