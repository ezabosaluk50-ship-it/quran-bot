import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔑 ضع توكن البوت هنا
TOKEN = "8285683997:AAEGtW87OC8XB0x7g75mhMM2iajYHc-p3uc"


# ✅ دالة تجيب رابط شغال تلقائيًا
def get_working_surah_url(surah_number):
    surah_number = str(surah_number).zfill(3)

    urls = [
        f"https://server10.mp3quran.net/islam_sobhi/{surah_number}.mp3",
        f"https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/{surah_number}.mp3",
        f"https://server6.mp3quran.net/islam_sobhi/{surah_number}.mp3"
    ]

    for url in urls:
        try:
            r = requests.head(url, timeout=3)
            if r.status_code == 200:
                return url
        except:
            continue

    return None


# 📖 أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 أهلاً بك في بوت القرآن الكريم\n\n"
        "استخدم الأمر:\n"
        "/surah رقم_السورة\n\n"
        "مثال:\n"
        "/surah 5"
    )


# 🎧 إرسال السورة
async def send_surah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        surah_number = int(context.args[0])
    except:
        await update.message.reply_text("❌ اكتب رقم السورة فقط\nمثال: /surah 5")
        return

    surah_name = f"رقم {surah_number}"

    url = get_working_surah_url(surah_number)

    if not url:
        await update.message.reply_text("❌ لم يتم العثور على السورة حالياً")
        return

    keyboard = [
        [
            InlineKeyboardButton("▶️ استماع", url=url),
            InlineKeyboardButton("📤 مشاركة", switch_inline_query=url)
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📖 سورة {surah_name}\n🎧 القارئ: إسلام صبحي",
        reply_markup=reply_markup
    )


# 🚀 تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("surah", send_surah))

print("✅ البوت يعمل الآن...")
app.run_polling()
