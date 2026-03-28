import os
import json
import random
import logging
import requests
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
USERS_FILE = "users.json"

# قائمة السور والقراء (نفس القائمة السابقة)
SURAHS = ["الفاتحة","البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم", "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة", "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج", "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس", "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص", "الفلق", "الناس"]
READERS_LIST = [("مشاري العفاسي", "https://server8.mp3quran.net/afs/"), ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"), ("عبد الباسط", "https://server7.mp3quran.net/basit/"), ("السديس", "https://server11.mp3quran.net/sds/"), ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"), ("إسلام صبحي", "https://server14.mp3quran.net/islam/"), ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"), ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"), ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"), ("فارس عباد", "https://server8.mp3quran.net/frs_a/"), ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"), ("خالد الجليل", "https://server10.mp3quran.net/jleel/")]

# دالة حفظ واسترجاع المفضل (تعمل مع Railway)
def get_user_data():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_fav(u_id, r_idx):
    data = get_user_data()
    data[str(u_id)] = {"fav": r_idx}
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# --- الدوال الأساسية ---
async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    u_id = update.effective_user.id

    if data.startswith("s_"):
        context.user_data["s"] = data.split("_")[1]
        # عرض القراء (3 في كل سطر)
        btns = []
        row = []
        for i, r in enumerate(READERS_LIST):
            row.append(InlineKeyboardButton(r[0], callback_data=f"r_{i}"))
            if len(row) == 3: btns.append(row); row = []
        if row: btns.append(row)
        await q.edit_message_text(f"📖 سورة {SURAHS[int(context.user_data['s'])-1]}\n🎙️ اختر القارئ:", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("r_"):
        r_idx = int(data.split("_")[1])
        s_num = context.user_data.get("s", "1")
        r_name, base_url = READERS_LIST[r_idx]
        save_fav(u_id, r_idx)
        
        status_msg = await q.edit_message_text(f"⏳ جاري تجهيز {SURAHS[int(s_num)-1]}... قد يستغرق ذلك دقيقة للسور الكبيرة.")
        audio_url = f"{base_url}{s_num.zfill(3)}.mp3"

        try:
            # الحل التقني: تحميل الملف للسيرفر ثم رفعه لتجاوز قيد الـ 20MB
            response = requests.get(audio_url, timeout=120)
            if response.status_code == 200:
                audio_file = BytesIO(response.content)
                audio_file.name = f"{SURAHS[int(s_num)-1]}.mp3"
                
                await context.bot.send_audio(
                    chat_id=q.message.chat_id,
                    audio=audio_file,
                    title=SURAHS[int(s_num)-1],
                    performer=r_name,
                    timeout=300 # وقت كافٍ للرفع
                )
                await status_msg.delete()
            else:
                raise Exception("فشل التحميل من السيرفر")
        except Exception as e:
            logging.error(e)
            await q.message.reply_text("❌ عذراً، تعذر إرسال السورة. تأكد من جودة اتصال السيرفر أو جرب قارئاً آخر.")

# (بقية الدوال Start و Text_handler تبقى كما هي في الكود السابق)
