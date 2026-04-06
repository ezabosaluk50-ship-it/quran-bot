import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
# ملف لحفظ الـ File IDs لسرعة الإرسال مستقبلاً
FILE_IDS_PATH = "file_ids.json"

# --- دالة تحميل وحفظ معرفات الملفات (للسرعة) ---
def load_file_ids():
    if os.path.exists(FILE_IDS_PATH):
        with open(FILE_IDS_PATH, "r") as f: return json.load(f)
    return {}

def save_file_id(surah_num, reader_idx, file_id):
    data = load_file_ids()
    key = f"{surah_num}_{reader_idx}"
    data[key] = file_id
    with open(FILE_IDS_PATH, "w") as f: json.dump(data, f)

# (نفس القوائم السابقة مع الاحتفاظ بـ SURAHS و READERS_LIST)
SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

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
    ("إسلام صبحي","https://server8.mp3quran.net/islam/"),
]

# ------------------- نظام الإرسال الذكي -------------------
async def smart_send_audio(update, context, surah_num, reader_idx):
    chat_id = update.effective_chat.id
    file_ids = load_file_ids()
    key = f"{surah_num}_{reader_idx}"
    
    reader_name, base_url = READERS_LIST[reader_idx]
    surah_name = SURAHS[surah_num-1]
    caption = f"📖 سورة {surah_name} \n🎙 القارئ {reader_name}"

    # 1. محاولة الإرسال باستخدام File ID (سرعة فائقة)
    if key in file_ids:
        try:
            await context.bot.send_audio(chat_id=chat_id, audio=file_ids[key], caption=caption)
            return
        except: pass # إذا انتهت صلاحية الـ ID ننتقل للرفع اليدوي

    # 2. الرفع اليدوي (إذا لم يوجد ID)
    sent_msg = await context.bot.send_message(chat_id=chat_id, text="⏳ جاري تحضير الملف لأول مرة...")
    surah_str = str(surah_num).zfill(3)
    audio_url = f"{base_url}{surah_str}.mp3"
    
    file_path = f"{surah_num}.mp3"
    try:
        r = requests.get(audio_url, timeout=60)
        with open(file_path, "wb") as f: f.write(r.content)
        with open(file_path, "rb") as audio:
            msg = await context.bot.send_audio(chat_id=chat_id, audio=audio, caption=caption)
            # حفظ الـ ID للمرة القادمة
            save_file_id(surah_num, reader_idx, msg.audio.file_id)
        await sent_msg.delete()
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="❌ عذراً، حدث خطأ في جلب السورة.")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

# --- معالجة البحث النصي ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in SURAHS:
        index = SURAHS.index(text) + 1
        context.user_data["surah"] = index
        # بناء لوحة القراء المرفقة في كودك الأصلي
        from __main__ import build_readers_keyboard 
        await update.message.reply_text(f"📖 سورة {text}\nاختر القارئ:", reply_markup=InlineKeyboardMarkup(build_readers_keyboard()))
    elif text == "🎲 سورة عشوائية":
        # منطق السورة العشوائية
        pass 

# (بقية الدوال Start و Callbacks مع استبدال send_audio بـ smart_send_audio)
