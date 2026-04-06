import os
import json
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# --- قائمة القراء وروابطهم ---
READERS_LIST = [
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط (مرتل)", "https://server7.mp3quran.net/basit/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("عبدالرحمن السديس", "https://server11.mp3quran.net/sds/"),
    ("محمد المنشاوي", "https://server10.mp3quran.net/minsh/"),
    ("هاني الرفاعي", "https://server8.mp3quran.net/hani/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/"),
    ("محمود الحصري", "https://server13.mp3quran.net/husr/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

ISLAM_SOBHI_AVAILABLE = {1, 2, 3, 12, 13, 14, 15, 18, 19, 20, 21, 24, 25, 26, 27, 30, 31, 32, 36, 41, 42, 43, 44, 47, 48, 50, 51, 52, 53, 54, 55, 56, 62, 67, 68, 70, 71, 72, 73, 74, 75, 77, 78, 79, 80, 81, 82, 85, 87, 88, 89, 90, 91, 93, 94, 95, 96, 97, 100, 101, 102, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114}

# الكيبورد الرئيسي مع إعادة كافة الأزرار
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📖 اختر سورة"), KeyboardButton("🎲 سورة عشوائية")],
        [KeyboardButton("🔍 بحث عن سورة"), KeyboardButton("⭐ قارئي المفضل")]
    ],
    resize_keyboard=True
)

def build_surah_keyboard(page=1):
    surahs_slice = SURAHS[:57] if page == 1 else SURAHS[57:]
    keyboard = []
    row = []
    for i, name in enumerate(surahs_slice):
        index = i+1 if page==1 else i+58
        row.append(InlineKeyboardButton(f"{index}. {name}", callback_data=f"surah_{index}"))
        if len(row) == 4:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    nav = [InlineKeyboardButton("التالي ◀️", callback_data="page_2")] if page==1 else [InlineKeyboardButton("▶️ السابق", callback_data="page_1")]
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def build_readers_keyboard():
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"reader_{i}"))
        if len(row) == 3:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌙 أهلاً بك في بوت القرآن الكريم 🌙", reply_markup=MAIN_KEYBOARD)
    await update.message.reply_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(1))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📖 اختر سورة":
        await update.message.reply_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(1))
    
    elif text == "🎲 سورة عشوائية":
        num = random.randint(1, 114)
        context.user_data["surah"] = num
        await update.message.reply_text(f"🎲 تم اختيار سورة {SURAHS[num-1]}، اختر القارئ:", reply_markup=build_readers_keyboard())
    
    elif text == "🔍 بحث عن سورة":
        await update.message.reply_text("أرسل اسم السورة التي تبحث عنها (مثال: الكهف):")
        context.user_data["state"] = "searching"
    
    elif text == "⭐ قارئي المفضل":
        fav = context.user_data.get("fav_reader_name", "لم تختر قارئاً بعد")
        await update.message.reply_text(f"⭐ قارئك المفضل حالياً هو: {fav}\nسيتم حفظ اختيارك القادم تلقائياً.")
    
    elif context.user_data.get("state") == "searching":
        found = False
        for i, name in enumerate(SURAHS):
            if text in name:
                context.user_data["surah"] = i + 1
                await update.message.reply_text(f"🔍 وجدنا سورة {name}، اختر القارئ:", reply_markup=build_readers_keyboard())
                found = True
                break
        if not found:
            await update.message.reply_text("❌ لم يتم العثور على السورة، تأكد من الكتابة بشكل صحيح.")
        context.user_data["state"] = None

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(page))
    
    elif data.startswith("surah_"):
        num = int(data.split("_")[1])
        context.user_data["surah"] = num
        await query.edit_message_text(f"🎙 اختر القارئ لسورة {SURAHS[num-1]}:", reply_markup=build_readers_keyboard())
    
    elif data == "random":
        num = random.randint(1, 114)
        context.user_data["surah"] = num
        await query.edit_message_text(f"🎲 سورة {SURAHS[num-1]}، اختر القارئ:", reply_markup=build_readers_keyboard())

    elif data.startswith("reader_"):
        reader_idx = int(data.split("_")[1])
        surah_num = context.user_data.get("surah", 1)
        reader_name, base_url = READERS_LIST[reader_idx]
        surah_name = SURAHS[surah_num-1]
        
        # حفظ القارئ المفضل
        context.user_data["fav_reader_name"] = reader_name

        if reader_name == "إسلام صبحي" and surah_num not in ISLAM_SOBHI_AVAILABLE:
            await query.edit_message_text(f"⚠️ سورة {surah_name} غير متوفرة بصوت إسلام صبحي حالياً.")
            return

        status_msg = await query.edit_message_text(f"⏳ جاري إرسال سورة {surah_name}...")
        audio_url = f"{base_url}{str(surah_num).zfill(3)}.mp3"
        
        try:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_url,
                title=f"سورة {surah_name}",
                performer=reader_name,
                caption=f"سورة {surah_name} - القارئ {reader_name}",
                filename=f"{surah_name}.mp3"
            )
            await status_msg.delete()
        except Exception:
            await context.bot.send_message(chat_id=query.message.chat_id, text="❌ عذراً، حدث خطأ في المصدر.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
