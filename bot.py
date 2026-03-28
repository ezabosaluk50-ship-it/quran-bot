import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
USERS_FILE = "users.json"

WELCOME_MESSAGE = """🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲"""

READERS_LIST = [
    ("مشاري العفاسي",  "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/"),
    ("ماهر المعيقلي",  "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط",     "https://server7.mp3quran.net/basit/"),
    ("السديس",         "https://server11.mp3quran.net/sds/"),
    ("سعد الغامدي",    "https://server7.mp3quran.net/s_gmd/"),
    ("ناصر القطامي",   "https://download.quranicaudio.com/quran/naasir_al-qataami/"),
    ("ياسر الدوسري",   "https://download.quranicaudio.com/quran/yasser_ad-dussary/"),
    ("إدريس أبكر",     "https://download.quranicaudio.com/quran/idrees_abkar/"),
    ("المنشاوي",       "https://download.quranicaudio.com/quran/muhammad_siddeeq_al-minshaawee/"),
    ("الحصري",         "https://download.quranicaudio.com/quran/mahmood_khaleel_al-husaree/"),
    ("أحمد العجمي",    "https://server10.mp3quran.net/ajm/"),
    ("خالد الجليل",    "https://download.quranicaudio.com/quran/khaalid_al-qahtaanee/"),
    ("فارس عباد",      "https://server8.mp3quran.net/frs_a/"),
    ("هاني الرفاعي",   "https://server8.mp3quran.net/hani/"),
    ("علي الحذيفي",    "https://server9.mp3quran.net/hthfi/"),
    ("إسلام صبحي",     "https://portalquran.com/file/islam/"),
    ("عبدالله الجهني", "https://download.quranicaudio.com/quran/abdullaah_3awwaad_al-juhaynee/"),
]

SURAHS = [
    "الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف",
    "الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر",
    "النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون",
    "النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان",
    "السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر",
    "فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح",
    "الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة",
    "الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون",
    "التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح",
    "الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات",
    "عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى",
    "الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين",
    "العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر",
    "الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد",
    "الإخلاص","الفلق","الناس"
]


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user(user_id, username, full_name):
    users = load_users()
    is_new = str(user_id) not in users
    if is_new:
        users[str(user_id)] = {"username": username, "name": full_name, "favorite_reader": None}
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    return is_new

def get_favorite_reader(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("favorite_reader")

def save_favorite_reader(user_id, reader_index):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]["favorite_reader"] = reader_index
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)


def build_surah_keyboard(page=1):
    if page == 1:
        surahs_slice = SURAHS[:57]
        start_idx = 1
    else:
        surahs_slice = SURAHS[57:]
        start_idx = 58
    keyboard = []
    row = []
    for i, name in enumerate(surahs_slice):
        num = start_idx + i
        row.append(InlineKeyboardButton(f"{num}. {name}", callback_data=f"surah_{num}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    if page == 1:
        keyboard.append([InlineKeyboardButton("🎲 سورة عشوائية", callback_data="random")])
        keyboard.append([
            InlineKeyboardButton("🔍 بحث", callback_data="search"),
            InlineKeyboardButton("التالي ◀️", callback_data="page_2"),
        ])
    else:
        keyboard.append([InlineKeyboardButton("🎲 سورة عشوائية", callback_data="random")])
        keyboard.append([
            InlineKeyboardButton("▶️ السابق", callback_data="page_1"),
            InlineKeyboardButton("🔍 بحث", callback_data="search"),
        ])
    return keyboard


def build_readers_keyboard(user_id=None):
    favorite = get_favorite_reader(user_id) if user_id else None
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        label = f"⭐ {name}" if i == favorite else name
        row.append(InlineKeyboardButton(label, callback_data=f"reader_{i}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return keyboard


# ✅✅✅ الدالة المعدلة الجديدة (هنا حل مشكلة السور الكبيرة) ✅✅✅
async def send_audio(context, chat_id, audio_url, caption):
    """
    دالة ذكية: ترسل الملف مباشرة إذا كان صغيراً، 
    أو ترسل الرابط إذا كان كبيراً (لتجاوز حد 50 ميجابايت)
    """
    try:
        # 1. فحص حجم الملف أولاً باستخدام طلب خفيف (HEAD)
        head_resp = requests.head(audio_url, timeout=10, allow_redirects=True)
        file_size = int(head_resp.headers.get('content-length', 0))
        
        # حد تلقرام للبوتات: 50 ميجابايت
        MAX_BOT_SIZE = 50 * 1024 * 1024
        
        if file_size < MAX_BOT_SIZE and file_size > 0:
            # ✅ الملف صغير: أرسله كصوتية مباشرة
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio_url,
                caption=caption,
                parse_mode="Markdown",
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
            )
            return True
        else:
            # ⚠️ الملف كبير: أرسل رابط التشغيل المباشر (يعمل كصوتية أيضاً)
            # هذه الطريقة "سرعة البرق" ولا تستهلك موارد البوت
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎧 استمع الآن", url=audio_url)]
            ])
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📖 {caption}\n\n⚠️ حجم السورة كبير، اضغط للاستماع المباشر:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return True
            
    except Exception as e:
        logging.error(f"Error in send_audio: {e}")
        # 2. حل احتياطي: إذا فشل أي شيء، أرسل الرابط كنص عادي
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📖 {caption}\n🔗 الرابط المباشر: {audio_url}",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            return True
        except:
            return False
# ✅✅✅ نهاية الدالة المعدلة ✅✅✅


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📖 اختر سورة"), KeyboardButton("🎲 سورة عشوائية")],
        [KeyboardButton("🔍 بحث عن سورة"), KeyboardButton("⭐ قارئي المفضل")],
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = save_user(user.id, user.username, user.full_name)
    context.user_data["searching"] = False

    if is_new:
        await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN_KEYBOARD)
    else:
        await update.message.reply_text("مرحباً بعودتك! 🌙", reply_markup=MAIN_KEYBOARD)

    favorite = get_favorite_reader(user.id)
    if favorite is not None:
        reader_name = READERS_LIST[favorite][0]
        await update.message.reply_text(f"⭐ قارئك المفضل: *{reader_name}*", parse_mode="Markdown")

    await update.message.reply_text(
        "📖 اختر السورة — الصفحة 1 (1-57):",
        reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1))
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if ADMIN_ID and user_id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return
    count = len(load_users())
    await update.message.reply_text(f"📊 *إحصائيات البوت*\n\n👥 عدد المستخدمين: *{count}*", parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📖 اختر سورة":
        await update.message.reply_text(
            "📖 اختر السورة — الصفحة 1 (1-57):",
            reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1))
        )
        return

    if text == "🎲 سورة عشوائية":
        import random
        surah_num = random.randint(1, 114)
        context.user_data["surah"] = str(surah_num)
        surah_name = SURAHS[surah_num - 1]
        await update.message.reply_text(
            f"🎲 *سورة عشوائية: {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard(update.effective_user.id)),
            parse_mode="Markdown"
        )
        return

    if text == "🔍 بحث عن سورة":
        context.user_data["searching"] = True
        await update.message.reply_text("🔍 اكتب اسم السورة:\n\nمثال: *كهف* أو *بقرة*", parse_mode="Markdown")
        return

    if text == "⭐ قارئي المفضل":
        favorite = get_favorite_reader(update.effective_user.id)
        if favorite is not None:
            reader_name = READERS_LIST[favorite][0]
            await update.message.reply_text(
                f"⭐ قارئك المفضل هو: *{reader_name}*\n\nاختر سورة للاستماع بصوته:",
                reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1)),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("لم تختر قارئاً مفضلاً بعد!\n\nاختر سورة واستمع لأي قارئ وسيُحفظ تلقائياً ⭐")
        return

    if not context.user_data.get("searching"):
        return
    query_text = update.message.text.strip()
    context.user_data["searching"] = False
    results = [(i + 1, name) for i, name in enumerate(SURAHS) if query_text in name]
    if not results:
        await update.message.reply_text(f"❌ لم أجد سورة باسم *{query_text}*\n\n/start للقائمة الكاملة.", parse_mode="Markdown")
        return
    keyboard = [[InlineKeyboardButton(f"{num}. {name}", callback_data=f"surah_{num}")] for num, name in results]
    await update.message.reply_text(f"🔍 نتائج البحث عن *{query_text}*:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "page_1":
        await query.edit_message_text("📖 اختر السورة — الصفحة 1 (1-57):", reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1)))

    elif data == "page_2":
        await query.edit_message_text("📖 اختر السورة — الصفحة 2 (58-114):", reply_markup=InlineKeyboardMarkup(build_surah_keyboard(2)))

    elif data == "random":
        surah_num = random.randint(1, 114)
        context.user_data["surah"] = str(surah_num)
        surah_name = SURAHS[surah_num - 1]
        await query.edit_message_text(
            f"🎲 *سورة عشوائية: {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard(user_id)),
            parse_mode="Markdown"
        )

    elif data == "search":
        context.user_data["searching"] = True
        await query.message.reply_text("🔍 اكتب اسم السورة:\n\nمثال: *كهف* أو *بقرة*", parse_mode="Markdown")

    elif data.startswith("surah_"):
        surah_num = data.split("_")[1]
        context.user_data["surah"] = surah_num
        context.user_data["searching"] = False
        surah_name = SURAHS[int(surah_num) - 1]
        await query.edit_message_text(
            f"📖 *سورة {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard(user_id)),
            parse_mode="Markdown"
        )

    elif data.startswith("reader_"):
        reader_index = int(data.split("_")[1])
        reader_name, server_url = READERS_LIST[reader_index]
        surah_num = context.user_data.get("surah", "1")
        surah_name = SURAHS[int(surah_num) - 1]
        save_favorite_reader(user_id, reader_index)
        await query.edit_message_text(f"⏳ جاري تحميل سورة *{surah_name}* بصوت *{reader_name}*...", parse_mode="Markdown")
        surah_str = str(surah_num).zfill(3)
        audio_url = f"{server_url}{surah_str}.mp3"
        caption = f"سورة *{surah_name}* — {reader_name}\n\n/start لسورة اخرى"
        
        # ✅✅✅ هنا نستخدم الدالة الجديدة المعدلة ✅✅✅
        success = await send_audio(context, query.message.chat_id, audio_url, caption)
        
        if success:
            me = await context.bot.get_me()
            share_text = f"استمع لسورة {surah_name} بصوت {reader_name} 🎧"
            share_link = f"https://t.me/share/url?url=https://t.me/{me.username}&text={share_text}"
            keyboard = [[InlineKeyboardButton("📤 شارك السورة", url=share_link)]]
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"📖 *{surah_name}* — {reader_name}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text("تعذر التحميل.\n/start للبدء من جديد")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
