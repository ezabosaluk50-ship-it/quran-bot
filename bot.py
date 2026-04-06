import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# --- قائمة السور المتاحة حصراً لإسلام صبحي (بناءً على الفحص) ---
ISLAM_SOBHI_AVAILABLE = {
    1, 2, 3, 5, 6, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 29, 30, 
    31, 32, 34, 35, 36, 38, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 
    58, 59, 60, 61, 62, 63, 64, 66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 
    82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 112, 113, 114
}

READERS_LIST = [
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط (مرتل)", "https://server7.mp3quran.net/basit/"),
    ("ناصر القطامي", "https://server6.mp3quran.net/qtm/"),
    ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"), # الرابط الجديد
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("إدريس أبكر", "https://server6.mp3quran.net/abkr/"),
    ("فارس عباد", "https://server8.mp3quran.net/frs_a/"),
    ("عبدالرحمن السديس", "https://server11.mp3quran.net/sds/"),
    ("محمد المنشاوي", "https://server10.mp3quran.net/minsh/"),
    ("هاني الرفاعي", "https://server8.mp3quran.net/hani/"),
    ("خالد الجليل", "https://server10.mp3quran.net/jleel/"),
    ("محمود الحصري", "https://server13.mp3quran.net/husr/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

# ... (دوال build_surah_keyboard و build_readers_keyboard و start تبقى كما هي) ...

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("reader_"):
        reader_idx = int(data.split("_")[1])
        surah_num = context.user_data.get("surah", 1)
        reader_name, base_url = READERS_LIST[reader_idx]
        surah_name = SURAHS[surah_num-1]

        # فحص خاص بإسلام صبحي
        if reader_name == "إسلام صبحي" and surah_num not in ISLAM_SOBHI_AVAILABLE:
            await query.edit_message_text(f"⚠️ عذراً، سورة {surah_name} لم تسجل بعد بصوت القارئ إسلام صبحي. يرجى اختيار قارئ آخر.")
            return

        status_msg = await query.edit_message_text(f"⏳ جاري إرسال سورة {surah_name} بصوت {reader_name}...")
        audio_url = f"{base_url}{str(surah_num).zfill(3)}.mp3"
        
        try:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_url,
                title=f"سورة {surah_name}",
                performer=reader_name,
                caption=f"📖 سورة {surah_name} \n🎙 القارئ {reader_name}",
                filename=f"سورة {surah_name}.mp3"
            )
            await status_msg.delete()
            if 'welcome_msg_id' in context.user_data:
                try: await context.bot.delete_message(chat_id=query.message.chat_id, message_id=context.user_data['welcome_msg_id'])
                except: pass
        except Exception:
            await context.bot.send_message(chat_id=query.message.chat_id, text="❌ حدث خطأ في المصدر، جرب قارئاً آخر.")
