import json
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "YOUR_BOT_TOKEN"

WELCOME_TEXT = """
🌙 أهلاً بك في بوت القرآن الكريم 🌙
🤍 استمع للقرآن الكريم بصوت نخبة من القرّاء في أي وقت
📖 اختر القارئ واستمتع بالتلاوة بخشوع
🎧 البوت يعمل في الخلفية لتستمر بالتصفح والاستماع معًا
📖 قال تعالى: "ألا بذكر الله تطمئن القلوب"
✨ شارك البوت لتكسب الأجر 🤲
"""

SURA_NAMES = {
    "001": "الفاتحة","002": "البقرة","003": "آل عمران","004": "النساء","005": "المائدة","006": "الأنعام",
    "007": "الأعراف","008": "الأنفال","009": "التوبة","010": "يونس","011": "هود","012": "يوسف",
    "013": "الرعد","014": "إبراهيم","015": "الحجر","016": "النحل","017": "الإسراء","018": "الكهف",
    "019": "مريم","020": "طه","021": "الأنبياء","022": "الحج","023": "المؤمنون","024": "النور",
    "025": "الفرقان","026": "الشعراء","027": "النمل","028": "القصص","029": "العنكبوت","030": "الروم",
    "031": "لقمان","032": "السجدة","033": "الأحزاب","034": "سبأ","035": "فاطر","036": "يس",
    "037": "الصافات","038": "ص","039": "الزمر","040": "غافر","041": "فصلت","042": "الشورى",
    "043": "الزخرف","044": "الدخان","045": "الجاثية","046": "الأحقاف","047": "محمد","048": "الفتح",
    "049": "الحجرات","050": "ق","051": "الذاريات","052": "الطور","053": "النجم","054": "القمر",
    "055": "الرحمن","056": "الواقعة","057": "الحديد","058": "المجادلة","059": "الحشر","060": "الممتحنة",
    "061": "الصف","062": "الجمعة","063": "المنافقون","064": "التغابن","065": "الطلاق","066": "التحريم",
    "067": "الملك","068": "القلم","069": "الحاقة","070": "المعارج","071": "نوح","072": "الجن",
    "073": "المزمل","074": "المدثر","075": "القيامة","076": "الإنسان","077": "المرسلات","078": "النبأ",
    "079": "النازعات","080": "عبس","081": "التكوير","082": "الانفطار","083": "المطففين","084": "الانشقاق",
    "085": "البروج","086": "الطارق","087": "الأعلى","088": "الغاشية","089": "الفجر","090": "البلد",
    "091": "الشمس","092": "الليل","093": "الضحى","094": "الشرح","095": "التين","096": "العلق",
    "097": "القدر","098": "البينة","099": "الزلزلة","100": "العاديات","101": "القارعة","102": "التكاثر",
    "103": "العصر","104": "الهمزة","105": "الفيل","106": "قريش","107": "الماعون","108": "الكوثر",
    "109": "الكافرون","110": "النصر","111": "المسد","112": "الإخلاص","113": "الفلق","114": "الناس"
}

READERS = {
    "مشاري العفاسي": "https://server8.mp3quran.net/afs/",
    "ماهر المعيقلي": "https://server12.mp3quran.net/maher/",
    "عبد الباسط": "https://server8.mp3quran.net/basit_mjwd/",
    "ناصر القطامي": "https://server6.mp3quran.net/qtm/",
    "سعد الغامدي": "https://server7.mp3quran.net/s_gmd/",
    "السديس": "https://server11.mp3quran.net/sds/",
    "المنشاوي": "https://server8.mp3quran.net/Minsh/",
    "إدريس أبكر": "https://server10.mp3quran.net/abkr/",
    "ياسر الدوسري": "https://server11.mp3quran.net/yasser/",
    "خالد الجليل": "https://server8.mp3quran.net/jleel/",
    "أحمد العجمي": "https://server8.mp3quran.net/ajm/",
    "الحصري": "https://server7.mp3quran.net/husr/",
    "علي الحذيفي": "https://server8.mp3quran.net/hthfi/",
    "هاني الرفاعي": "https://server8.mp3quran.net/rafi/",
    "فارس عباد": "https://server8.mp3quran.net/frs_a/",
    "عبدالله الجهني": "https://server8.mp3quran.net/jhn/",
    "إسلام صبحي": "https://download.quranicaudio.com/quran/IslamSobhi/"
}

USER_FAVORITE = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 قائمة القرّاء", callback_data="readers")],
        [InlineKeyboardButton("⭐ قارئك المفضل", callback_data="fav")],
        [InlineKeyboardButton("🎲 سورة عشوائية", callback_data="random")],
        [InlineKeyboardButton("🔍 بحث عن سورة", callback_data="search")]
    ])

def readers_menu():
    buttons = []
    row = []
    for name in READERS.keys():
        row.append(InlineKeyboardButton(name, callback_data=f"reader:{name}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 الرئيسية", callback_data="home")])
    return InlineKeyboardMarkup(buttons)

def surah_menu(page, reader):
    surahs = list(SURA_NAMES.items())
    page1 = surahs[:57]
    page2 = surahs[57:]
    current = page1 if page == 1 else page2

    buttons = [
        [InlineKeyboardButton(name, callback_data=f"sura:{reader}:{num}")]
        for num, name in current
    ]

    nav = []
    if page == 1:
        nav.append(InlineKeyboardButton("▶ الصفحة التالية", callback_data=f"page:2:{reader}"))
    else:
        nav.append(InlineKeyboardButton("◀ الصفحة السابقة", callback_data=f"page:1:{reader}"))

    buttons.append(nav)
    buttons.append([
        InlineKeyboardButton("🏠 الرئيسية", callback_data="home"),
        InlineKeyboardButton("🔙 رجوع", callback_data="readers")
    ])

    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu())

async def search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    for num, name in SURA_NAMES.items():
        if query == name:
            fav = USER_FAVORITE.get(update.message.from_user.id, None)
            reader = fav if fav else random.choice(list(READERS.keys()))
            url = READERS[reader] + f"{num}.mp3"
            await update.message.reply_audio(url, caption=f"{name} — {reader}")
            return
    await update.message.reply_text("❌ لم يتم العثور على السورة")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "home":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=main_menu())

    elif data == "readers":
        await query.edit_message_text("اختر القارئ:", reply_markup=readers_menu())

    elif data.startswith("reader:"):
        reader = data.split(":")[1]
        USER_FAVORITE[query.from_user.id] = reader
        await query.edit_message_text(f"اختر السورة ({reader}):", reply_markup=surah_menu(1, reader))

    elif data.startswith("page:"):
        _, page, reader = data.split(":")
        await query.edit_message_text(f"اختر السورة ({reader}):", reply_markup=surah_menu(int(page), reader))

    elif data.startswith("sura:"):
        _, reader, num = data.split(":")
        url = READERS[reader] + f"{num}.mp3"
        await query.message.reply_audio(url, caption=f"{SURA_NAMES[num]} — {reader}")

    elif data == "fav":
        fav = USER_FAVORITE.get(query.from_user.id, None)
        if not fav:
            await query.edit_message_text("❌ لم يتم اختيار قارئ مفضل بعد", reply_markup=main_menu())
        else:
            await query.edit_message_text(f"اختر السورة ({fav}):", reply_markup=surah_menu(1, fav))

    elif data == "random":
        fav = USER_FAVORITE.get(query.from_user.id, random.choice(list(READERS.keys())))
        num = str(random.randint(1, 114)).zfill(3)
        url = READERS[fav] + f"{num}.mp3"
        await query.message.reply_audio(url, caption=f"{SURA_NAMES[num]} — {fav}")

    elif data == "search":
        await query.edit_message_text("🔍 اكتب اسم السورة الآن:")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_message))
    await app.run_polling()

import asyncio
asyncio.run(main())
