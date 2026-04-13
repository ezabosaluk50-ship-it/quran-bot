import os
import random
import logging
import requests
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
USERS_FILE = "users_list.txt"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_user(user_id):
    user_str = str(user_id)
    if user_str not in seen_users:
        seen_users.add(user_str)
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_str}\n")

seen_users = load_users()

READERS_LIST = [
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط عبد الصمد", "https://server7.mp3quran.net/basit/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("عبدالرحمن السديس", "https://server11.mp3quran.net/sds/"),
    ("محمد المنشاوي", "https://server10.mp3quran.net/minsh/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/"),
    ("محمود الحصري", "https://server13.mp3quran.net/husr/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("ابدأ 💙"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("🎲 سورة عشوائية"), KeyboardButton("🔍 بحث")]
    ], resize_keyboard=True)

def build_surah_keyboard(page=1):
    start, end = (0, 57) if page == 1 else (57, 114)
    keyboard = []
    row = []
    for i in range(start, end):
        row.append(InlineKeyboardButton(f"{i+1}. {SURAHS[i]}", callback_data=f"surah_{i+1}"))
        if len(row) == 3: keyboard.append(row); row = []
    if row: keyboard.append(row)
    nav = [InlineKeyboardButton("التالي ◀️", callback_data="page_2") if page == 1 else InlineKeyboardButton("▶️ السابق", callback_data="page_1")]
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def build_readers_keyboard():
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"reader_{i}"))
        if len(row) == 2: keyboard.append(row); row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if str(user_id) not in seen_users:
        welcome_message = (
            "✨ **مرحباً بك في بوت القرآن الكريم** ✨\n\n"
            "قال رسول الله ﷺ: «اقرؤوا القرآن فإنه يأتي يوم القيامة شفيعاً لأصحابه».\n\n"
            "📖 **اختر الآن السورة التي تود الاستماع إليها:**"
        )
        # نحفظ معرف رسالة الترحيب لحذفها لاحقاً
        sent_msg = await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard(), parse_mode='Markdown')
        context.user_data["welcome_msg_id"] = sent_msg.message_id
        
        surah_msg = await update.message.reply_text("قائمة السور المتاحة:", reply_markup=build_surah_keyboard(1))
        context.user_data["last_menu_id"] = surah_msg.message_id
        save_user(user_id)
    else:
        await update.message.reply_text("📖 قائمة السور:", reply_markup=get_main_keyboard())
        surah_msg = await update.message.reply_text("اختر سورة:", reply_markup=build_surah_keyboard(1))
        context.user_data["last_menu_id"] = surah_msg.message_id

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(seen_users)
    await update.message.reply_text(f"📊 **إحصائيات البوت:**\n\n👥 عدد المستخدمين الكلي: {count}", parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("page_"):
        await query.edit_message_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(int(data.split("_")[1])))
    elif data.startswith("surah_"):
        context.user_data["s_num"] = int(data.split("_")[1])
        await query.edit_message_text(f"🎙 اختر القارئ لسورة {SURAHS[context.user_data['s_num']-1]}:", reply_markup=build_readers_keyboard())
    elif data.startswith("reader_"):
        idx = int(data.split("_")[1])
        s_num = context.user_data.get("s_num", 1)
        r_name, r_url = READERS_LIST[idx]
        
        # --- ميزة المسح التلقائي لرسالة الترحيب والقائمة ---
        try:
            # مسح رسالة الترحيب (إن وجدت)
            if "welcome_msg_id" in context.user_data:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data["welcome_msg_id"])
                del context.user_data["welcome_msg_id"]
        except: pass

        msg = await query.edit_message_text(f"⏳ جاري تجهيز سورة {SURAHS[s_num-1]} بصوت {r_name}...")
        
        servers = [r_url, r_url.replace("server10", "server11"), r_url.replace("server10", "server6")]
        success = False
        for base_url in servers:
            file_url = f"{base_url}{str(s_num).zfill(3)}.mp3"
            try:
                resp = requests.get(file_url, timeout=15)
                if resp.status_code == 200:
                    audio_content = BytesIO(resp.content)
                    audio_content.name = f"{SURAHS[s_num-1]}.mp3"
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=audio_content, title=f"سورة {SURAHS[s_num-1]}", performer=r_name)
                    await msg.delete() # حذف رسالة "جاري التجهيز" بعد الإرسال
                    success = True
                    break
            except: continue
        if not success: await msg.edit_text("❌ الملف غير متوفر حالياً.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "ابدأ 💙":
        await start_logic(update, context)
    elif text == "📖 اختر سورة":
        surah_msg = await update.message.reply_text("📖 قائمة السور:", reply_markup=build_surah_keyboard(1))
        context.user_data["last_menu_id"] = surah_msg.message_id
    elif text == "🎲 سورة عشوائية":
        num = random.randint(1, 114)
        context.user_data["s_num"] = num
        await update.message.reply_text(f"🎲 سورة {SURAHS[num-1]}، اختر القارئ:", reply_markup=build_readers_keyboard())
    elif text == "🔍 بحث":
        await update.message.reply_text("أرسل اسم السورة للبحث عنها:")
        context.user_data["searching"] = True
    elif context.user_data.get("searching"):
        for i, name in enumerate(SURAHS):
            if text in name:
                context.user_data["s_num"] = i + 1
                await update.message.reply_text(f"✅ وجدنا سورة {name}، اختر القارئ:", reply_markup=build_readers_keyboard())
                context.user_data["searching"] = False
                return

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_logic))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
