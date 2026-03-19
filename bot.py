import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

READERS_LIST = [
    ("عبد الباسط عبد الصمد", "abdul_basit_murattal"),
    ("ماهر المعيقلي",        "maher_al_muaiqly"),
    ("مشاري العفاسي",        "mishaari_raashid_al_3afaasee"),
    ("عبد الرحمن السديس",    "abdurrahmaan_as-sudais"),
    ("سعد الغامدي",          "sa3d_al-ghaamidi"),
]

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for i, name in enumerate(SURAHS, 1):
        row.append(InlineKeyboardButton(f"{i}. {name}", callback_data=f"surah_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    await update.message.reply_text(
        "🕌 *بوت القرآن الكريم*\n\nاختر السورة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("surah_"):
        surah_num = data.split("_")[1]
        context.user_data["surah"] = surah_num
        surah_name = SURAHS[int(surah_num) - 1]
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"reader_{i}")]
            for i, (name, _) in enumerate(READERS_LIST)
        ]
        await query.edit_message_text(
            f"📖 *سورة {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("reader_"):
        reader_index = int(data.split("_")[1])
        reader_name, reader_id = READERS_LIST[reader_index]
        surah_num = context.user_data.get("surah", "1")
        surah_name = SURAHS[int(surah_num) - 1]

        await query.edit_message_text(
            f"⏳ جاري تحميل سورة *{surah_name}* بصوت *{reader_name}*...",
            parse_mode="Markdown"
        )
        surah_str = str(surah_num).zfill(3)
        audio_url = f"https://download.quranicaudio.com/quran/{reader_id}/{surah_str}.mp3"
        logging.info(f"Fetching: {audio_url}")
        try:
            await query.message.reply_voice(
                voice=audio_url,
                caption=f"سورة *{surah_name}* — {reader_name}\n\n/start لسورة اخرى",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error: {e}")
            await query.message.reply_text(f"تعذر التحميل: {str(e)[:100]}\n/start للبدء من جديد")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
