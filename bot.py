import os
import json
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. إعداد السجلات (ستظهر لك في Logs في Railway)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. جلب التوكن (تأكد من ضبطه في Railway باسم BOT_TOKEN)
TOKEN = os.environ.get("BOT_TOKEN")

# 3. الـ ID الخاص بك (سنقوم باختباره الآن)
ADMIN_ID = 5410915902 

USER_FILE = "users.json"

# --- وظائف قاعدة البيانات ---
def get_stats():
    if not os.path.exists(USER_FILE): return 0
    try:
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            return len(data) if isinstance(data, list) else 0
    except: return 0

def save_user(user_id):
    users = []
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                users = json.load(f)
        except: users = []
    if user_id not in users:
        users.append(user_id)
        with open(USER_FILE, "w") as f:
            json.dump(users, f)

# --- الكيبورد ---
def get_main_keyboard(user_id):
    # جعلنا الزر يظهر للجميع مؤقتاً فقط لنفحص هل يعمل الضغط عليه أم لا
    buttons = [
        [KeyboardButton("ابدأ 🤍"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("📊 الإحصائيات")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# --- الدوال التنفيذية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    logging.info(f"User {user_id} started the bot")
    await update.message.reply_text(
        f"أهلاً بك!\nرقم الـ ID الخاص بك هو: {user_id}", # سيخبرك برقمك فوراً
        reply_markup=get_main_keyboard(user_id)
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"Stats requested by {user_id}")
    
    if user_id == ADMIN_ID:
        count = get_stats()
        await update.message.reply_text(f"📊 إحصائيات الإدارة:\nالمستخدمون: {count}")
    else:
        # إذا لم تكن الإداره، سيخبرك البوت بذلك بدلاً من الصمت
        await update.message.reply_text(f"⚠️ صلاحيات محدودة.\nرقمك: {user_id}\nالمطلوب: {ADMIN_ID}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # فحص النصوص يدوياً لضمان عدم حدوث خطأ في الإيموجي
    if "ابدأ" in text:
        await start(update, context)
    elif "إحصائيات" in text:
        await stats_command(update, context)
    else:
        await update.message.reply_text(f"وصلتني رسالتك: {text}")

if __name__ == "__main__":
    if not TOKEN:
        print("CRITICAL ERROR: BOT_TOKEN is missing!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()

        # ترتيب الهاندرز مهم جداً
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", stats_command))
        
        # التقاط الأزرار والنصوص
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

        print("Bot is starting...")
        app.run_polling()
