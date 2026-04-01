import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================
#   إعدادات البوت
# ============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# ============================
#   قائمة القرّاء
# ============================

READERS = {
    "alafasy": "العفاسي",
    "sudais": "السديس",
    "minshawi": "المنشاوي",
    "husary": "الحصري",
    "basit": "الباسيط",
    "idris_abkar": "إدريس أبكر",
    "nasser_alqatami": "ناصر القطامي",
    "abdullah_aljuhany": "عبدالله الجهني",
    "saad_alghamdi": "سعد الغامدي",
    "yasser_aldosari": "ياسر الدوسري",
    "khalid_aljalil": "خالد الجليل",
    "ahmad_alajmi": "أحمد العجمي",
    "ali_alhuthaifi": "علي الحذيفي",
    "hani_alrifai": "هاني الرفاعي",
    "fares_abbad": "فارس عباد",
    "islam_sobhi": "إسلام صبحي"
}

# ============================
#   الرسالة الترحيبية
# ============================

WELCOME_TEXT = """
🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲
"""

# ============================
#   أوامر البوت
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []

    for key, name in READERS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"reader:{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔗 مشاركة البوت", switch_inline_query="")])

    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def reader_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reader_key = query.data.split(":")[1]
    context.user_data["reader"] = reader_key

    keyboard = []
    row = []

    for i in range(1, 115):
        surah_num = str(i).zfill(3)
        row.append(InlineKeyboardButton(surah_num, callback_data=f"surah:{surah_num}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await query.edit_message_text(
        f"اختر السورة بصوت: {READERS[reader_key]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def surah_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    surah_num = query.data.split(":")[1]
    reader = context.user_data.get("reader")

    file_path = f"audio/{reader}/{surah_num}.mp3"

    if not os.path.exists(file_path):
        await query.edit_message_text("⚠️ السورة غير موجودة!")
        return

    await query.message.reply_audio(audio=open(file_path, "rb"))
    await query.edit_message_text("✔️ تم إرسال السورة")

# ============================
#   تشغيل البوت
# ============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reader_selected, pattern="reader:"))
    app.add_handler(CallbackQueryHandler(surah_selected, pattern="surah:"))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
