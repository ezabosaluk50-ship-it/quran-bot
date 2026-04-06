import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# --- رسالة الترحيب القديمة ---
WELCOME_MESSAGE = """🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲"""

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

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/start")],
        [KeyboardButton("📖 اختر سورة"), KeyboardButton("🎲 سورة عشوائية")],
        [KeyboardButton("🔍 بحث عن سورة"), KeyboardButton("⭐ قارئي المفضل")]
    ],
    resize_keyboard=True
)

def build_surah_keyboard(page=1):
    surahs_slice = SURAHS[:57] if page == 1 else SURAHS[57:]
    keyboard = []
    row = []
    for i, name in enumerate(surahs_slice):
        index = i+1 if page==1 else i+58
        row.append(InlineKeyboardButton(name, callback_data=f"surah_{index}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    nav = [InlineKeyboardButton("التالي ◀️", callback_data="page_2")] if page==1 else [InlineKeyboardButton("▶️ السابق", callback_data="page_1")]
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def build_readers_keyboard():
    keyboard = []
    row = []
    for i, (name, _) in enumerate(READERS_LIST):
        row.append(InlineKeyboardButton(name, callback_data=f"reader_{i}"))
        if len(row) == 3: # 3 قراء في كل سطر كما طلبت
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(WELCOME_MESSAGE, reply_markup=MAIN_KEYBOARD)
    context.user_data['welcome_msg_id'] = msg.message_id
    await update.message.reply_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(1))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(page))
    elif data.startswith("surah_"):
        num = int(data.split("_")[1])
        context.user_data["surah"] = num
        await query.edit_message_text(f"🎙 اختر القارئ لسورة {SURAHS[num-1]}:", reply_markup=build_readers_keyboard())
    elif data.startswith("reader_"):
        reader_idx = int(data.split("_")[1])
        surah_num = context.user_data.get("surah", 1)
        reader_name, base_url = READERS_LIST[reader_idx]
        surah_name = SURAHS[surah_num-1]
        
        status_msg = await query.edit_message_text(f"⏳ جاري تحميل سورة {surah_name} بصوت {reader_name}...")
        
        audio_url = f"{base_url}{str(surah_num).zfill(3)}.mp3"
        # تم تعديل اسم الملف ليظهر بالعربي عند الإرسال
        file_path = f"سورة {surah_name}.mp3" 
        
        try:
            r = requests.get(audio_url, stream=True)
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            with open(file_path, "rb") as audio:
                # إرسال الملف بالاسم العربي المسجل في file_path
                await context.bot.send_audio(
                    chat_id=query.message.chat_id, 
                    audio=audio, 
                    caption=f"سورة {surah_name} - القارئ {reader_name}",
                    filename=f"سورة {surah_name}.mp3"
                )
            
            # حذف الرسائل بعد الإرسال بنجاح
            await status_msg.delete()
            if 'welcome_msg_id' in context.user_data:
                try:
                    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['welcome_msg_id'])
                except: pass
                
        except Exception:
            await context.bot.send_message(chat_id=query.message.chat_id, text="❌ عذراً، حدث خطأ أثناء تحميل السورة.")
        finally:
            if os.path.exists(file_path): 
                os.remove(file_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
