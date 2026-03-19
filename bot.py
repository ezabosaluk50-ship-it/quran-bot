import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

READERS = {
    "عبد الباسط عبد الصمد": "1",
    "ماهر المعيقلي":        "69",
    "مشاري العفاسي":        "10",
    "عبد الرحمن السديس":    "6",
    "سعد الغامدي":          "9",
}

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


def start(update: Update, context: CallbackContext):
    keyboard = []
    row = []
    for i, name in enumerate(SURAHS, 1):
        row.append(InlineKeyboardButton(f"{i}. {name}", callback_data=f"surah_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    update.message.reply_text(
        "🕌 *بوت القرآن الكريم*\n\nاختر السورة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith("surah_"):
        surah_num = data.split("_")[1]
        context.user_data["surah"] = surah_num
        surah_name = SURAHS[int(surah_num) - 1]
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"reader_{rid}")]
            for name, rid in READERS.items()
        ]
        query.edit_message_text(
            f"📖 *سورة {surah_name}*\n\nاختر القارئ:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("reader_"):
        reader_id = data.split("_")[1]
        surah_num = context.user_data.get("surah", "1")
        surah_name = SURAHS[int(surah_num) - 1]
        reader_name = next(n for n, i in READERS.items() if i == reader_id)
        query.edit_message_text(
            f"⏳ جاري تحميل سورة *{surah_name}* بصوت *{reader_name}*...",
            parse_mode="Markdown"
        )
        surah_str = str(surah_num).zfill(3)
        audio_url = f"https://server8.mp3quran.net/{reader_id}/{surah_str}.mp3"
        try:
            query.message.reply_voice(
                voice=audio_url,
                caption=f"🎙️ سورة *{surah_name}* — {reader_name}\n\n/start لسورة أخرى",
                parse_mode="Markdown"
            )
        except Exception:
            query.message.reply_text("⚠️ تعذّر التحميل، جرّب قارئاً آخر.\n/start للبدء من جديد")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
