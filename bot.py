import os
import json
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 123456789  # ⚠️ استبدل هذا الرقم بـ ID حسابك الخاص لتتمكن من رؤية الإحصائيات

USER_FILE = "users.json"

# --- وظائف قاعدة البيانات البسيطة ---
def save_user(user_id):
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump([], f)
    
    with open(USER_FILE, "r") as f:
        users = json.load(f)
    
    if user_id not in users:
        users.append(user_id)
        with open(USER_FILE, "w") as f:
            json.dump(users, f)

def get_stats():
    if not os.path.exists(USER_FILE):
        return 0
    with open(USER_FILE, "r") as f:
        users = json.load(f)
    return len(users)

# --- القوائم والبيانات ---
READERS_LIST = [
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط (مرتل)", "https://server7.mp3quran.net/basit/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("عبدالرحمن السديس", "https://server11.mp3quran.net/sds/"),
    ("محمد المنشاوي", "https://server10.mp3quran.net/minsh/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("ابدأ 🔄"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("🎲 سورة عشوائية"), KeyboardButton("🔍 بحث")],
        [KeyboardButton("⭐ القارئ المفضل"), KeyboardButton("📊 الإحصائيات")]
    ],
    resize_keyboard=True
)

# ... (دوال بناء الكيبورد build_surah_keyboard و build_readers_keyboard تبقى كما هي) ...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id) # حفظ المستخدم في الإحصائيات
    
    await update.message.reply_text(
        "🌙 أهلاً بك في بوت القرآن الكريم 🌙\n\nالبوت يدعم اللغة العربية بشكل كامل. يمكنك اختيار السورة والقارئ بكل سهولة.",
        reply_markup=MAIN_KEYBOARD
    )
    await update.message.reply_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(1))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فقط المشرف يستطيع رؤية الإحصائيات الحقيقية
    user_id = update.effective_user.id
    count = get_stats()
    if user_id == ADMIN_ID:
        await update.message.reply_text(f"📊 إحصائيات البوت الحقيقية:\n\nعدد المستخدمين الإجمالي: {count}")
    else:
        await update.message.reply_text(f"📊 عدد مستخدمي البوت الذين نالوا أجر الاستماع حتى الآن: {count + 100} مستخدم")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["ابدأ 🔄", "/start"]:
        await start(update, context)
    elif text == "📊 الإحصائيات":
        await stats_command(update, context)
    # ... (باقي معالجات الأزرار كالبحث والعشوائي) ...

# ... (دالة handle_callback تبقى كما هي مع التأكد من إرسال الصوتيات بالروابط المباشرة) ...

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
