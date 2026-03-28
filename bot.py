import os
import json
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# جلب الإعدادات من Railway Variables
TOKEN = os.environ.get("BOT_TOKEN")
USERS_FILE = "users.json"

# رسالة الترحيب الخاصة بك
WELCOME_MESSAGE = """🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲"""

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

READERS_LIST = [
    ("مشاري العفاسي",  "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي",  "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط",     "https://server7.mp3quran.net/basit/"),
    ("السديس",         "https://server11.mp3quran.net/sds/"),
    ("سعد الغامدي",    "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي",     "https://server14.mp3quran.net/islam/"),
    ("ياسر الدوسري",   "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر",     "https://server6.mp3quran.net/abkr/"),
    ("أحمد العجمي",    "https://server10.mp3quran.net/ajm/"),
    ("فارس عباد",      "https://server8.mp3quran.net/frs_a/"),
    ("ناصر القطامي",   "https://server6.mp3quran.net/qtm/"),
    ("خالد الجليل",    "https://server10.mp3quran.net/jleel/")
]

# --- لوحة التحكم السفلية ---
MAIN_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("📖 اختر سورة"), KeyboardButton("🎲 سورة عشوائية")],
    [KeyboardButton("🔍 بحث عن سورة"), KeyboardButton("⭐ قارئي المفضل")]
], resize_keyboard=True)

# --- وظائف المساعدة ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_user(user_id, fav=None):
    users = load_users()
    u_id = str(user_id)
    if u_id not in users: users[u_id] = {"fav": None}
    if fav is not None: users[u_id]["fav"] = fav
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)

def get_surah_kb(page=1):
    start_idx = 1 if page == 1 else 58
    end_idx = 58 if page == 1 else 115
    keyboard = []
    row = []
    for i in range(start_idx, end_idx):
        row.append(InlineKeyboardButton(f"{i}. {SURAHS[i-1]}", callback_data=f"s_{i}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    nav = [InlineKeyboardButton("التالي ◀️" if page==1 else "▶️ السابق", callback_data=f"p_{2 if page==1 else 1}")]
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def get_readers_kb():
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"r_{i}"))
        if len(row) == 3: # ترتيب 3 قراء في كل سطر
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# --- المحركات الأساسية ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN_KEYBOARD)
    await update.message.reply_text("📖 اختر السورة المرجوة:", reply_markup=get_surah_kb(1))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📖 اختر سورة":
        await update.message.reply_text("📖 اختر السورة:", reply_markup=get_surah_kb(1))
    elif text == "🎲 سورة عشوائية":
        num = random.randint(1, 114)
        context.user_data["s"] = str(num)
        await update.message.reply_text(f"🎲 سورة مختارة: {SURAHS[num-1]}\n🎙️ اختر القارئ الآن:", reply_markup=get_readers_kb())
    elif text == "🔍 بحث عن سورة":
        context.user_data["searching"] = True
        await update.message.reply_text("🔍 اكتب اسم السورة التي تبحث عنها:")
    elif text == "⭐ قارئي المفضل":
        users = load_users()
        fav = users.get(str(user_id), {}).get("fav")
        if fav is not None:
            await update.message.reply_text(f"⭐ قارئك المفضل حالياً: {READERS_LIST[fav][0]}\n📖 اختر سورة للاستماع بصوته:", reply_markup=get_surah_kb(1))
        else:
            await update.message.reply_text("لم تختر قارئاً مفضلاً بعد. اختر سورة ثم قارئ وسيتم حفظه تلقائياً.")
    elif context.user_data.get("searching"):
        context.user_data["searching"] = False
        results = [(i+1, name) for i, name in enumerate(SURAHS) if text in name]
        if results:
            btns = [[InlineKeyboardButton(f"{n}. {nm}", callback_data=f"s_{n}")] for n, nm in results]
            await update.message.reply_text(f"🔍 نتائج البحث عن '{text}':", reply_markup=InlineKeyboardMarkup(btns))
        else:
            await update.message.reply_text("❌ لم أجد سورة بهذا الاسم.")

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = update.effective_user.id

    if data.startswith("p_"):
        p = int(data.split("_")[1])
        await q.edit_message_text(f"📖 صفحة {p}:", reply_markup=get_surah_kb(p))
    
    elif data.startswith("s_"):
        context.user_data["s"] = data.split("_")[1]
        surah_name = SURAHS[int(context.user_data['s'])-1]
        await q.edit_message_text(f"📖 سورة {surah_name}\n🎙️ اختر القارئ:", reply_markup=get_readers_kb())
        
    elif data.startswith("r_"):
        r_idx = int(data.split("_")[1])
        s_num = context.user_data.get("s", "1")
        r_name, url = READERS_LIST[r_idx]
        save_user(user_id, r_idx)
        
        msg = await q.edit_message_text(f"⏳ جاري تجهيز سورة {SURAHS[int(s_num)-1]} بصوت {r_name}...")
        
        try:
            full_url = f"{url}{s_num.zfill(3)}.mp3"
            await context.bot.send_audio(
                chat_id=q.message.chat_id, 
                audio=full_url, 
                title=SURAHS[int(s_num)-1], 
                performer=r_name,
                caption=f"✅ استماعاً طيباً\n🎙️ {r_name}\n\n/start للعودة"
            )
            await msg.delete()
        except:
            await q.message.reply_text("❌ عذراً، تعذر الإرسال. قد يكون الملف كبيراً جداً أو الرابط مؤقتاً.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()
