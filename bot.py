import os
import logging
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

READERS_LIST = [
    ("مشاري العفاسي",        "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي",        "https://server8.mp3quran.net/maher/"),
    ("عبد الباسط عبد الصمد", "https://server7.mp3quran.net/basit/"),
    ("عبد الرحمن السديس",    "https://server11.mp3quran.net/sds/"),
    ("سعد الغامدي",          "https://server7.mp3quran.net/s_gmd/"),
    ("ناصر القطامي",         "https://server8.mp3quran.net/qtm/"),
    ("ياسر الدوسري",         "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر",           "https://server13.mp3quran.net/abkr/"),
    ("محمد صديق المنشاوي",   "https://server10.mp3quran.net/minsh/"),
    ("محمود خليل الحصري",    "https://server7.mp3quran.net/husr/"),
    ("أحمد العجمي",          "https://server11.mp3quran.net/ajm/"),
    ("خالد الجليل",          "https://server8.mp3quran.net/jlil/"),
    ("فارس عباد",            "https://server7.mp3quran.net/frs/"),
    ("هاني الرفاعي",         "https://server8.mp3quran.net/hani/"),
    ("إسلام صبحي",           "https://server10.mp3quran.net/islam/"),
    ("علي الحذيفي",          "https://server11.mp3quran.net/a_hzfy/"),
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)
    keyboard = []
    row = []
    for i, name in enumerate(SURAHS, 1):
        row.append(InlineKeyboardButton(f"{i}. {name}", callback_data=f"surah_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
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
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"reader_{i}")]
            for i, (name, _) in enumerate(READERS_LIST)
        ]
        await query.edit_message_text(
            f"📖 *سورة {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(keyboard),
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
            await query.message.reply_text("تعذر التحميل، السورة غير متوفرة لهذا القارئ.\n/start للبدء من جديد")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
