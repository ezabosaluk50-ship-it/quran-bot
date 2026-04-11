import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة الأداء
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# --- قائمة القراء المحدثة بأدق الروابط ---
READERS_LIST = [
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("عبد الباسط عبد الصمد", "https://server7.mp3quran.net/basit/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

# --- لوحة المفاتيح الرئيسية ---
def get_main_keyboard():
    buttons = [
        [KeyboardButton("ابدأ 🤍"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("🎲 سورة عشوائية"), KeyboardButton("🔍 بحث")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# بناء كيبورد السور (صفحتين لسهولة العرض)
def build_surah_keyboard(page=1):
    surahs_slice = SURAHS[:57] if page == 1 else SURAHS[57:]
    keyboard = []
    row = []
    for i, name in enumerate(surahs_slice):
        index = i + 1 if page == 1 else i + 58
        row.append(InlineKeyboardButton(f"{index}. {name}", callback_data=f"surah_{index}"))
        if len(row) == 3:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    
    # أزرار التنقل
    nav_buttons = []
    if page == 1: nav_buttons.append(InlineKeyboardButton("الصفحة التالية ◀️", callback_data="page_2"))
    else: nav_buttons.append(InlineKeyboardButton("▶️ الصفحة السابقة", callback_data="page_1"))
    keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(keyboard)

# بناء كيبورد القراء
def build_readers_keyboard():
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"reader_{i}"))
        if len(row) == 2:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# --- معالجة الأحداث ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ مرحباً بك في بوت القرآن الكريم ✨\nاضغط على 'اختر سورة' للبدء.",
        reply_markup=get_main_keyboard()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(page))

    elif data.startswith("surah_"):
        surah_idx = int(data.split("_")[1])
        context.user_data["current_surah"] = surah_idx
        await query.edit_message_text(
            f"🎙 اختر القارئ لسورة {SURAHS[surah_idx-1]}:",
            reply_markup=build_readers_keyboard()
        )

    elif data.startswith("reader_"):
        reader_idx = int(data.split("_")[1])
        surah_num = context.user_data.get("current_surah", 1)
        reader_name, base_url = READERS_LIST[reader_idx]
        
        # الرابط المباشر للملف الصوتي
        audio_url = f"{base_url}{str(surah_num).zfill(3)}.mp3"
        
        # إرسال الملف
        try:
            await query.message.reply_text(f"⏳ جاري تحميل سورة {SURAHS[surah_num-1]} بصوت {reader_name}...")
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_url,
                title=f"سورة {SURAHS[surah_num-1]}",
                performer=reader_name
            )
        except Exception as e:
            await query.message.reply_text(f"❌ عذراً، حدث خطأ في تشغيل هذا الملف. قد يكون السيرفر متوقفاً حالياً.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "ابدأ" in text or text == "/start":
        await start(update, context)
    elif text == "📖 اختر سورة":
        await update.message.reply_text("📖 اختر السورة المطلوبة:", reply_markup=build_surah_keyboard(1))
    elif text == "🎲 سورة عشوائية":
        num = random.randint(1, 114)
        context.user_data["current_surah"] = num
        await update.message.reply_text(f"🎲 سورة {SURAHS[num-1]}، اختر القارئ:", reply_markup=build_readers_keyboard())
    elif text == "🔍 بحث":
        await update.message.reply_text("أرسل اسم السورة التي تبحث عنها:")
        context.user_data["state"] = "searching"
    elif context.user_data.get("state") == "searching":
        for i, name in enumerate(SURAHS):
            if text in name:
                context.user_data["current_surah"] = i + 1
                await update.message.reply_text(f"✅ وجدنا سورة {name}، اختر القارئ:", reply_markup=build_readers_keyboard())
                context.user_data["state"] = None
                return
        await update.message.reply_text("❌ لم نعثر على سورة بهذا الاسم، حاول مرة أخرى.")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.run_polling()
