import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود")

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

SURAHS = [
"الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر",
"النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم",
"لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف",
"محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف",
"الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة",
"الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية",
"الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر",
"الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"
]

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/start")],
        [KeyboardButton("📖 اختر سورة"), KeyboardButton("🎲 سورة عشوائية")],
        [KeyboardButton("🔍 بحث عن سورة"), KeyboardButton("⭐ قارئي المفضل")]
    ],
    resize_keyboard=True
)

# ----------------- وظائف المستخدمين -----------------
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_user(user_id, username, full_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"username": username, "name": full_name, "favorite_reader": None}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

def get_favorite_reader(user_id):
    return load_users().get(str(user_id), {}).get("favorite_reader")

def save_favorite_reader(user_id, reader_index):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]["favorite_reader"] = reader_index
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

# ----------------- إرسال الصوت -----------------
async def send_audio(context, chat_id, audio_url, caption, surah_name, retries=3):
    file_name = f"{surah_name}.mp3"
    attempt = 0
    while attempt < retries:
        try:
            with requests.get(audio_url, stream=True, timeout=60) as r:
                if r.status_code != 200:
                    attempt += 1
                    continue
                with open(file_name, "wb") as f:
                    for chunk in r.iter_content(1024*1024):
                        if chunk:
                            f.write(chunk)
            with open(file_name, "rb") as audio:
                await context.bot.send_audio(chat_id=chat_id, audio=audio, caption=caption)
            return True
        except:
            attempt += 1
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
    await context.bot.send_message(chat_id, f"❌ فشل إرسال {surah_name}")
    return False

# ----------------- واجهات -----------------
def build_surah_keyboard(page=1):
    if page == 1:
        surahs_slice = SURAHS[:57]
    else:
        surahs_slice = SURAHS[57:]
    keyboard = []
    row = []
    for i, name in enumerate(surahs_slice):
        index = i+1 if page==1 else i+58
        row.append(InlineKeyboardButton(f"{index}. {name}", callback_data=f"surah_{index}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    nav_buttons = []
    if page == 1:
        nav_buttons.append(InlineKeyboardButton("التالي ◀️", callback_data="page_2"))
    else:
        nav_buttons.append(InlineKeyboardButton("▶️ السابق", callback_data="page_1"))
    nav_buttons.append(InlineKeyboardButton("🎲 سورة عشوائية", callback_data="random"))
    keyboard.append(nav_buttons)
    return keyboard

def build_readers_keyboard(user_id=None):
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"reader_{i}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return keyboard

# ----------------- /start -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.full_name)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN_KEYBOARD)
    await update.message.reply_text("📖 اختر السورة:", reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1)))

# ----------------- التعامل مع أزرار لوحة المفاتيح -----------------
async def handle_keyboard_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎲 سورة عشوائية":
        num = random.randint(1, 114)
        context.user_data["surah"] = num
        await update.message.reply_text(
            f"🎲 سورة {SURAHS[num-1]}",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard())
        )

    elif text == "⭐ قارئي المفضل":
        fav = get_favorite_reader(user_id)
        if fav is not None:
            await update.message.reply_text(f"⭐ قارئك المفضل: {READERS_LIST[fav][0]}")
        else:
            await update.message.reply_text("❌ لم تختر قارئ مفضل بعد")

    elif text == "🔍 بحث عن سورة":
        context.user_data["search_mode"] = True
        await update.message.reply_text("🔍 اكتب اسم السورة للبحث")

    elif context.user_data.get("search_mode"):
        context.user_data["search_mode"] = False
        query = text.strip()
        results = [(i+1, s) for i,s in enumerate(SURAHS) if query in s]
        if not results:
            await update.message.reply_text("❌ لم يتم العثور على السورة")
            return
        keyboard = [[InlineKeyboardButton(name, callback_data=f"surah_{i}")] for i,name in results]
        await update.message.reply_text("📖 نتائج البحث:", reply_markup=InlineKeyboardMarkup(keyboard))

# ----------------- callback -----------------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # صفحة السور
    if data.startswith("page_"):
        page = 1 if data == "page_1" else 2
        await query.edit_message_text("📖 اختر السورة:", reply_markup=InlineKeyboardMarkup(build_surah_keyboard(page)))

    # سورة عشوائية
    elif data == "random":
        num = random.randint(1, 114)
        context.user_data["surah"] = num
        await query.edit_message_text(f"🎲 سورة {SURAHS[num-1]}", reply_markup=InlineKeyboardMarkup(build_readers_keyboard()))

    # اختيار سورة
    elif data.startswith("surah_"):
        num = int(data.split("_")[1])
        context.user_data["surah"] = num
        await query.edit_message_text(f"📖 سورة {SURAHS[num-1]}", reply_markup=InlineKeyboardMarkup(build_readers_keyboard()))

    # اختيار قارئ
    elif data.startswith("reader_"):
        reader_index = int(data.split("_")[1])
        save_favorite_reader(user_id, reader_index)
        reader_name, url = READERS_LIST[reader_index]
        surah = context.user_data.get("surah", 1)
        surah_name = SURAHS[surah-1]
        surah_str = str(surah).zfill(3)
        await query.edit_message_text("⏳ جاري التحميل...")
        await send_audio(context, query.message.chat_id, f"{url}{surah_str}.mp3", f"{surah_name} - {reader_name}", surah_name)

# ----------------- تشغيل البوت -----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_keyboard_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
