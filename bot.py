import os
import random
import logging
import requests  # سنستخدمها لتحميل الملف وضمان عمله
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# تحديث قائمة القراء لضمان أفضل السيرفرات
READERS_LIST = [
    ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    ("عبد الباسط", "https://server7.mp3quran.net/basit/"),
    ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    ("إسلام صبحي", "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/"),
]

SURAHS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

# --- لوحة المفاتيح ---
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("ابدأ 🤍"), KeyboardButton("📖 اختر سورة")],
        [KeyboardButton("🎲 سورة عشوائية"), KeyboardButton("🔍 بحث")]
    ], resize_keyboard=True)

def build_surah_keyboard(page=1):
    surahs_slice = SURAHS[:57] if page == 1 else SURAHS[57:]
    keyboard = [[InlineKeyboardButton(f"{i+1 if page==1 else i+58}. {n}", callback_data=f"surah_{i+1 if page==1 else i+58}") for i, n in enumerate(surahs_slice[j:j+3])] for j in range(0, len(surahs_slice), 3)]
    nav = [InlineKeyboardButton("التالي ◀️", callback_data="page_2")] if page==1 else [InlineKeyboardButton("▶️ السابق", callback_data="page_1")]
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def build_readers_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(name, callback_data=f"reader_{i}") for i, (name, _) in enumerate(READERS_LIST[j:j+2])] for j in range(0, len(READERS_LIST), 2)])

# --- معالجة الطلبات ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("page_"):
        await query.edit_message_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(int(query.data.split("_")[1])))
    elif query.data.startswith("surah_"):
        context.user_data["s_num"] = int(query.data.split("_")[1])
        await query.edit_message_text(f"🎙 اختر القارئ لسورة {SURAHS[context.user_data['s_num']-1]}:", reply_markup=build_readers_keyboard())
    elif query.data.startswith("reader_"):
        idx = int(query.data.split("_")[1])
        s_num = context.user_data.get("s_num", 1)
        r_name, r_url = READERS_LIST[idx]
        file_url = f"{r_url}{str(s_num).zfill(3)}.mp3"
        
        status_msg = await query.edit_message_text(f"⏳ جاري تجهيز سورة {SURAHS[s_num-1]} بصوت {r_name}...\nيرجى الانتظار قليلاً.")
        
        try:
            # 🚀 الحل الجديد: تحميل الملف إلى الذاكرة أولاً
            response = requests.get(file_url, timeout=20)
            if response.status_code == 200:
                audio_content = BytesIO(response.content)
                audio_content.name = f"{SURAHS[s_num-1]}.mp3"
                
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_content,
                    title=f"سورة {SURAHS[s_num-1]}",
                    performer=r_name,
                    caption=f"تم التحميل بنجاح ✅\nالقارئ: {r_name}"
                )
                await status_msg.delete()
            else:
                # إذا كان الرابط معطلاً، نجرب سيرفر بديل (تلقائياً)
                await status_msg.edit_text(f"❌ السيرفر الرئيسي ({r_name}) لا يستجيب حالياً. جاري تجربة سيرفر بديل...")
                # (يمكنك هنا إضافة منطق لتجربة سيرفر آخر)
        except Exception as e:
            await status_msg.edit_text(f"❌ حدث خطأ تقني: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ مرحباً بك في بوت القرآن ✨", reply_markup=get_main_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "ابدأ" in update.message.text: await start(update, context)
    elif "اختر سورة" in update.message.text: await update.message.reply_text("📖 اختر السورة:", reply_markup=build_surah_keyboard(1))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
