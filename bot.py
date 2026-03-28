import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة الأخطاء في Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
USERS_FILE = "/tmp/users.json"  # استخدام مجلد tmp في سيرفرات الاستضافة لضمان صلاحيات الكتابة

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

READERS_LIST = [
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط", "https://server7.mp3quran.net/basit/"),
    ("السديس", "https://server11.mp3quran.net/sds/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/")
]

# --- إدارة البيانات ---
def save_fav(u_id, r_idx):
    try:
        data = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[str(u_id)] = r_idx
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except: pass

def get_fav(u_id):
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get(str(u_id))
    except: return None

# --- لوحات المفاتيح ---
def get_surah_kb(page=1):
    start, end = (1, 58) if page == 1 else (58, 115)
    btns = [[InlineKeyboardButton(f"{i}. {SURAHS[i-1]}", callback_data=f"s_{i}") for i in range(j, min(j+3, end))] for j in range(start, end, 3)]
    btns.append([InlineKeyboardButton("التالي ◀️" if page==1 else "▶️ السابق", callback_data=f"p_{2 if page==1 else 1}")])
    return InlineKeyboardMarkup(btns)

def get_readers_kb():
    btns = [[InlineKeyboardButton(READERS_LIST[i][0], callback_data=f"r_{i}"), 
             InlineKeyboardButton(READERS_LIST[i+1][0], callback_data=f"r_{i+1}"),
             InlineKeyboardButton(READERS_LIST[i+2][0], callback_data=f"r_{i+2}")] for i in range(0, len(READERS_LIST), 3)]
    return InlineKeyboardMarkup(btns)

# --- معالجة الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([["📖 اختر سورة", "🎲 سورة عشوائية"], ["🔍 بحث عن سورة", "⭐ قارئي المفضل"]], resize_keyboard=True)
    await update.message.reply_text("🌙 أهلاً بك في بوت القرآن الكريم", reply_markup=kb)
    await update.message.reply_text("📖 اختر السورة المرجوة:", reply_markup=get_surah_kb(1))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📖 اختر سورة":
        await update.message.reply_text("📖 قائمة السور:", reply_markup=get_surah_kb(1))
    elif text == "🎲 سورة عشوائية":
        n = random.randint(1, 114)
        context.user_data["s"] = str(n)
        await update.message.reply_text(f"🎲 سورة {SURAHS[n-1]}\n🎙️ اختر القارئ:", reply_markup=get_readers_kb())
    elif text == "⭐ قارئي المفضل":
        fav = get_fav(update.effective_user.id)
        if fav is not None:
            await update.message.reply_text(f"⭐ قارئك المفضل: {READERS_LIST[fav][0]}\n📖 اختر السورة الآن:", reply_markup=get_surah_kb(1))
        else:
            await update.message.reply_text("❌ لم تختر قارئاً بعد. اختر سورة ثم قارئ وسيتم حفظه.")
    elif text == "🔍 بحث عن سورة":
        context.user_data["search"] = True
        await update.message.reply_text("🔍 اكتب اسم السورة:")
    elif context.user_data.get("search"):
        context.user_data["search"] = False
        res = [(i+1, n) for i, n in enumerate(SURAHS) if text in n]
        if res:
            btns = [[InlineKeyboardButton(f"{n}. {nm}", callback_data=f"s_{n}")] for n, nm in res]
            await update.message.reply_text("🔍 نتائج البحث:", reply_markup=InlineKeyboardMarkup(btns))
        else: await update.message.reply_text("❌ لم أجدها.")

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("p_"):
        p = int(q.data.split("_")[1])
        await q.edit_message_text(f"📖 صفحة {p}:", reply_markup=get_surah_kb(p))
    elif q.data.startswith("s_"):
        context.user_data["s"] = q.data.split("_")[1]
        await q.edit_message_text(f"📖 سورة {SURAHS[int(context.user_data['s'])-1]}\n🎙️ اختر القارئ:", reply_markup=get_readers_kb())
    elif q.data.startswith("r_"):
        r_idx = int(q.data.split("_")[1])
        s_num = context.user_data.get("s", "1")
        r_name, url = READERS_LIST[r_idx]
        save_fav(update.effective_user.id, r_idx)
        
        # رسالة انتظار
        msg = await q.edit_message_text(f"⏳ جاري تجهيز {SURAHS[int(s_num)-1]}...")
        
        # رابط الملف
        audio_url = f"{url}{s_num.zfill(3)}.mp3"
        
        try:
            # نستخدم send_audio المباشر مع زيادة الـ Timeout بشكل كبير جداً للسور الكبيرة
            await context.bot.send_audio(
                chat_id=q.message.chat_id,
                audio=audio_url,
                title=SURAHS[int(s_num)-1],
                performer=r_name,
                connect_timeout=120, # وقت طويل للاتصال
                read_timeout=120,    # وقت طويل للتحميل
                write_timeout=120
