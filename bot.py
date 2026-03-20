import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

WELCOME_MESSAGE = """🌙 أهلاً وسهلاً بك في بوت القرآن الكريم 🌙
🤍 هذا البوت مخصص للاستماع إلى القرآن الكريم بصوت نخبة من أجمل القرّاء، لتعيش مع آيات الله في أي وقت وأي مكان
📖 اختر القارئ الذي تحب، واستمع بخشوع وتدبّر، واجعل القرآن رفيقك اليومي قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ لا تحرم غيرك من الأجر شارك البوت مع أصدقائك وأهلك، فربما آية يسمعها أحدهم تكون سببًا في هدايته، ويكون لك مثل أجره 🤲
🤍 نسأل الله أن يجعل هذا العمل صدقة جارية لنا ولكم، وأن يرزقنا وإياكم حب القرآن والعمل به
🎧 ابدأ الآن واستمع لكلام الله بصوتك المفضل"""

# القراء المختارين مع معرفاتهم من API الرسمي
SELECTED_READERS = {
    "مشاري العفاسي":        10,
    "ماهر المعيقلي":        69,
    "عبد الباسط عبد الصمد": 1,
    "عبد الرحمن السديس":    6,
    "سعد الغامدي":          9,
    "ناصر القطامي":         14,
    "ياسر الدوسري":         196,
    "إدريس أبكر":           46,
    "محمد صديق المنشاوي":   5,
    "محمود خليل الحصري":    4,
    "أحمد العجمي":          7,
    "خالد الجليل":          107,
    "فارس عباد":            76,
    "هاني الرفاعي":         17,
    "علي الحذيفي":          21,
    "عبدالله الجهني":        160,
}

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

# كاش للقراء
READERS_CACHE = {}

def get_reader_server(reader_id):
    if reader_id in READERS_CACHE:
        return READERS_CACHE[reader_id]
    try:
        url = f"https://www.mp3quran.net/api/v3/reciters?language=ar&reciter={reader_id}&rewaya=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("reciters"):
            server = data["reciters"][0]["moshaf"][0]["server"]
            READERS_CACHE[reader_id] = server
            return server
    except Exception as e:
        logging.error(f"API error: {e}")
    return None

READERS_LIST = list(SELECTED_READERS.items())


def build_keyboard(items, cols, prefix):
    keyboard = []
    row = []
    for i, item in enumerate(items):
        label = item if isinstance(item, str) else item[0]
        idx = i + 1 if prefix == "surah_" else i
        row.append(InlineKeyboardButton(label, callback_data=f"{prefix}{idx}"))
        if len(row) == cols:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)
    keyboard = build_keyboard(SURAHS, 4, "surah_")
    await update.message.reply_text(
        "📖 اختر السورة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("surah_"):
        surah_num = data.split("_")[1]
        context.user_data["surah"] = surah_num
        surah_name = SURAHS[int(surah_num) - 1]
        keyboard = build_keyboard(READERS_LIST, 3, "reader_")
        await query.edit_message_text(
            f"📖 *سورة {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("reader_"):
        reader_index = int(data.split("_")[1])
        reader_name, reader_id = READERS_LIST[reader_index]
        surah_num = context.user_data.get("surah", "1")
        surah_name = SURAHS[int(surah_num) - 1]

        await query.edit_message_text(
            f"⏳ جاري تحميل سورة *{surah_name}* بصوت *{reader_name}*...",
            parse_mode="Markdown"
        )

        server = get_reader_server(reader_id)
        if not server:
            await query.message.reply_text("تعذر الاتصال بالخادم.\n/start للبدء من جديد")
            return

        surah_str = str(surah_num).zfill(3)
        audio_url = f"{server}{surah_str}.mp3"
        logging.info(f"Fetching: {audio_url}")
        try:
            await query.message.reply_voice(
                voice=audio_url,
                caption=f"سورة *{surah_name}* — {reader_name}\n\n/start لسورة اخرى",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error: {e}")
            await query.message.reply_text("تعذر التحميل، السورة غير متوفرة لهذا القارئ.\n/start للبدء من جديد")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
