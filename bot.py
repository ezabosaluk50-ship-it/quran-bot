import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
USERS_FILE = "users.json"

WELCOME_MESSAGE = """🌙 أهلاً وسهلاً بك في بوت القرآن الكريم 🌙
🤍 هذا البوت مخصص للاستماع إلى القرآن الكريم بصوت نخبة من أجمل القرّاء، لتعيش مع آيات الله في أي وقت وأي مكان
📖 اختر القارئ الذي تحب، واستمع بخشوع وتدبّر، واجعل القرآن رفيقك اليومي قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ لا تحرم غيرك من الأجر شارك البوت مع أصدقائك وأهلك، فربما آية يسمعها أحدهم تكون سببًا في هدايته، ويكون لك مثل أجره 🤲
🤍 نسأل الله أن يجعل هذا العمل صدقة جارية لنا ولكم، وأن يرزقنا وإياكم حب القرآن والعمل به
🎧 ابدأ الآن واستمع لكلام الله بصوتك المفضل"""

READERS_LIST = [
    ("مشاري العفاسي",        "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي",        "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط عبد الصمد", "https://server7.mp3quran.net/basit/"),
    ("عبد الرحمن السديس",    "https://server11.mp3quran.net/sds/"),
    ("سعد الغامدي",          "https://server7.mp3quran.net/s_gmd/"),
    ("ناصر القطامي",         "https://server6.mp3quran.net/qtm/"),
    ("ياسر الدوسري",         "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر",           "https://server6.mp3quran.net/abkr/"),
    ("محمد صديق المنشاوي",   "https://server10.mp3quran.net/minsh/"),
    ("محمود خليل الحصري",    "https://server13.mp3quran.net/husr/"),
    ("أحمد العجمي",          "https://server10.mp3quran.net/ajm/"),
    ("خالد الجليل",          "https://server10.mp3quran.net/jleel/"),
    ("فارس عباد",            "https://server8.mp3quran.net/frs_a/"),
    ("هاني الرفاعي",         "https://server8.mp3quran.net/hani/"),
    ("علي الحذيفي",          "https://server9.mp3quran.net/hthfi/"),
    ("إسلام صبحي",           "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
    ("عبدالله الجهني",        "https://server13.mp3quran.net/jhn/"),
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
    users[str(user_id)] = {"username": username, "name": full_name}
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
        nav = [
            InlineKeyboardButton("🔍 بحث عن سورة", callback_data="search"),
            InlineKeyboardButton("التالي ◀️", callback_data="page_2"),
        ]
    else:
        nav = [
            InlineKeyboardButton("▶️ السابق", callback_data="page_1"),
            InlineKeyboardButton("🔍 بحث عن سورة", callback_data="search"),
        ]
    keyboard.append(nav)
    return keyboard


def build_readers_keyboard():
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.full_name)
    context.user_data["searching"] = False

    await update.message.reply_text(WELCOME_MESSAGE)
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
    await update.message.reply_text(
        f"📊 *إحصائيات البوت*\n\n👥 عدد المستخدمين: *{count}*",
        parse_mode="Markdown"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("searching"):
        return

    query_text = update.message.text.strip()
    context.user_data["searching"] = False

    results = [
        (i + 1, name) for i, name in enumerate(SURAHS)
        if query_text in name
    ]

    if not results:
        await update.message.reply_text(
            f"❌ لم أجد سورة باسم *{query_text}*\n\nجرّب اسماً آخر أو اكتب /start للقائمة الكاملة.",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton(f"{num}. {name}", callback_data=f"surah_{num}")]
        for num, name in results
    ]
    await update.message.reply_text(
        f"🔍 نتائج البحث عن *{query_text}*:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "page_1":
        await query.edit_message_text(
            "📖 اختر السورة — الصفحة 1 (1-57):",
            reply_markup=InlineKeyboardMarkup(build_surah_keyboard(1))
        )

    elif data == "page_2":
        await query.edit_message_text(
            "📖 اختر السورة — الصفحة 2 (58-114):",
            reply_markup=InlineKeyboardMarkup(build_surah_keyboard(2))
        )

    elif data == "search":
        context.user_data["searching"] = True
        await query.message.reply_text(
            "🔍 اكتب اسم السورة أو جزء منه:\n\nمثال: *كهف* أو *بقرة*",
            parse_mode="Markdown"
        )

    elif data.startswith("surah_"):
        surah_num = data.split("_")[1]
        context.user_data["surah"] = surah_num
        context.user_data["searching"] = False
        surah_name = SURAHS[int(surah_num) - 1]
        await query.edit_message_text(
            f"📖 *سورة {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(build_readers_keyboard()),
            parse_mode="Markdown"
        )

    elif data.startswith("reader_"):
        reader_index = int(data.split("_")[1])
        reader_name, server_url = READERS_LIST[reader_index]
        surah_num = context.user_data.get("surah", "1")
        surah_name = SURAHS[int(surah_num) - 1]

        await query.edit_message_text(
            f"⏳ جاري تحميل سورة *{surah_name}* بصوت *{reader_name}*...",
            parse_mode="Markdown"
        )
        surah_str = str(surah_num).zfill(3)
        audio_url = f"{server_url}{surah_str}.mp3"
        logging.info(f"Fetching: {audio_url}")
        try:
            await query.message.reply_voice(
                voice=audio_url,
                caption=f"سورة *{surah_name}* — {reader_name}\n\n/start لسورة اخرى",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error: {e}")
            await query.message.reply_text(
                "تعذر التحميل، السورة غير متوفرة لهذا القارئ.\n/start للبدء من جديد"
            )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
