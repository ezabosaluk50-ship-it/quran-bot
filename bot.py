import os
import json
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# ⚠️ تأكد أن هذا هو رقمك الصحيح
ADMIN_ID = 5410915902 

USER_FILE = "users.json"

# --- وظائف الإحصائيات ---
def get_stats():
    if not os.path.exists(USER_FILE): return 0
    with open(USER_FILE, "r") as f:
        try:
            data = json.load(f)
            return len(data)
        except: return 0

def save_user(user_id):
    users = []
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            try: users = json.load(f)
            except: users = []
    if user_id not in users:
        users.append(user_id)
        with open(USER_FILE, "w") as f:
            json.dump(users, f)

# --- لوحة المفاتيح ---
def get_main_keyboard(user_id):
    buttons = [
        [KeyboardButton("ابدأ 🤍"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("🎲 سورة عشوائية"), KeyboardButton("🔍 بحث")]
    ]
    # الزر يظهر لك وحدك في القائمة
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton("📊 الإحصائيات")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# --- الدوال البرمجية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text(
        "🌙 أهلاً بك في بوت القرآن الكريم 🌙", 
        reply_markup=get_main_keyboard(user_id)
    )

async def stats_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هذه الدالة هي المسؤولة عن تشغيل /stats"""
    user_id = update.effective_user.id
    
    # التحقق الصارم من الهوية
    if user_id == ADMIN_ID:
        count = get_stats()
        await update.message.reply_text(f"📊 إحصائيات البوت للمشرف:\nعدد المستخدمين الحاليين: {count}")
    else:
        # للمستخدمين العاديين: البوت لا يرد بشيء أو يرسل رسالة عادية
        return

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if "ابدأ" in text:
        await start(update, context)
    elif "إحصائيات" in text:
        # تشغيل الإحصائيات إذا ضغطت على الزر
        await stats_logic(update, context)

# --- التشغيل الرئيسي ---
if __name__ == "__main__":
    if not TOKEN:
        print("خطأ: لم يتم العثور على TOKEN")
    else:
        app = ApplicationBuilder().token(TOKEN).build()

        # 1. تفعيل أمر /start
        app.add_handler(CommandHandler("start", start))
        
        # 2. تفعيل أمر /stats (هذا ما طلبته تحديداً)
        app.add_handler(CommandHandler("stats", stats_logic))
        
        # 3. معالجة النصوص والأزرار
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

        print("البوت يعمل الآن...")
        app.run_polling()
