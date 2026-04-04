import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود")

USERS_FILE = "users.json"

WELCOME_MESSAGE = """🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲"""

# ✅ تم تعديل إسلام صبحي فقط
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
    ("خالد الجليل","https://download.quranicaudio.com/quran/khaalid_al-qahtaanee/"),
    ("أحمد العجمي","https://server10.mp3quran.net/ajm/"),
    ("الحصري","https://download.quranicaudio.com/quran/mahmood_khaleel_al-husaree/"),
    ("علي الحذيفي","https://server9.mp3quran.net/hthfi/"),
    ("هاني الرفاعي","https://server8.mp3quran.net/hani/"),
    ("فارس عباد","https://server8.mp3quran.net/frs_a/"),
    ("عبدالله الجهني","https://download.quranicaudio.com/quran/abdullaah_3awwaad_al-juhaynee/"),

    # 🔥 الحل هنا
    ("إسلام صبحي","ISLAM_SOBHI_SPECIAL"),
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
    ],
    resize_keyboard=True
)

# ✅ دالة خاصة لإسلام صبحي
def get_islam_sobhi_url(surah):
    surah = str(surah).zfill(3)
    urls = [
        f"https://server10.mp3quran.net/islam_sobhi/{surah}.mp3",
        f"https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/{surah}.mp3",
        f"https://server6.mp3quran.net/islam_sobhi/{surah}.mp3"
    ]
    for url in urls:
        try:
            r = requests.head(url, timeout=3)
            if r.status_code == 200:
                return url
        except:
            continue
    return None

# إرسال الصوت
async def send_audio(context, chat_id, audio_url, caption, surah_name):
    try:
        with requests.get(audio_url, stream=True, timeout=60) as r:
            if r.status_code != 200:
                await context.bot.send_message(chat_id, "❌ فشل تحميل السورة")
                return
            file_name = f"{surah_name}.mp3"
            with open(file_name, "wb") as f:
                for chunk in r.iter_content(1024*1024):
                    if chunk:
                        f.write(chunk)

        with open(file_name, "rb") as audio:
            await context.bot.send_audio(chat_id=chat_id, audio=audio, caption=caption)

        os.remove(file_name)

    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ خطأ: {e}")

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN_KEYBOARD)

# callback
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("surah_"):
        num = int(data.split("_")[1])
        context.user_data["surah"] = num

        keyboard = []
        for i, (name, _) in enumerate(READERS_LIST):
            keyboard.append([InlineKeyboardButton(name, callback_data=f"reader_{i}")])

        await query.edit_message_text(f"📖 سورة {SURAHS[num-1]}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("reader_"):
        reader_index = int(data.split("_")[1])
        reader_name, base_url = READERS_LIST[reader_index]

        surah = context.user_data.get("surah", 1)
        surah_name = SURAHS[surah-1]
        surah_str = str(surah).zfill(3)

        await query.edit_message_text("⏳ جاري التحميل...")

        # 🔥 الحل هنا
        if base_url == "ISLAM_SOBHI_SPECIAL":
            audio_url = get_islam_sobhi_url(surah)
        else:
            audio_url = f"{base_url}{surah_str}.mp3"

        if not audio_url:
            await query.message.reply_text("❌ لم يتم العثور على رابط يعمل")
            return

        await send_audio(context, query.message.chat_id, audio_url, f"{surah_name} - {reader_name}", surah_name)

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))

print("✅ البوت يعمل...")
app.run_polling()
