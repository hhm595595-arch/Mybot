import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


def religious_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📖 القرآن الكريم", callback_data="rel_quran")],
        [InlineKeyboardButton(text="📿 الأذكار اليومية", callback_data="rel_adhkar")],
        [InlineKeyboardButton(text="🤲 أدعية مأثورة", callback_data="rel_dua")],
        [InlineKeyboardButton(text="🔙 العودة", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


SURAH_NAMES = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام",
    "الأعراف", "الأنفال", "التوبة", "يونس", "هود", "يوسف",
    "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف",
    "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور",
    "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس",
    "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى",
    "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح",
    "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر",
    "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم",
    "الملك", "القلم", "الحاقة", "المعارج", "نوح", "الجن",
    "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ",
    "النازعات", "عبس", "التكوير", "الانفطار", "المطففين", "الانشقاق",
    "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق",
    "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر",
    "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر",
    "الكافرون", "النصر", "المسد", "الإخلاص", "الفلق", "الناس",
]

ADHKAR_MORNING = [
    "🤍 <b>أصبحنا وأصبح الملك لله</b>\nوالحمد لله، لا إله إلا الله وحده لا شريك له",
    "🤍 <b>اللهم بك أصبحنا وبك أمسينا</b>\nوبك نحيا وبك نموت وإليك النشور",
    "🤍 <b>اللهم إني أسألك العفو والعافية</b>\nفي الدنيا والآخرة",
    "🤍 <b>اللهم عافني في بدني</b>\nاللهم عافني في سمعي، اللهم عافني في بصري",
    "🤍 <b>رضيت بالله رباً</b>\nوبالإسلام ديناً، وبمحمد ﷺ نبياً",
    "🤍 <b>سبحان الله وبحمده</b>\nعدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته",
    "🤍 <b>لا إله إلا الله وحده لا شريك له</b>\nله الملك وله الحمد وهو على كل شيء قدير",
    "🤍 <b>اللهم صل وسلم على نبينا محمد</b>\nوعلى آله وصحبه أجمعين",
]

ADHKAR_EVENING = [
    "🌙 <b>أمسينا وأمسى الملك لله</b>\nوالحمد لله، لا إله إلا الله وحده لا شريك له",
    "🌙 <b>اللهم بك أمسينا وبك أصبحنا</b>\nوبك نحيا وبك نموت وإليك المصير",
    "🌙 <b>اللهم إني أسألك العفو والعافية</b>\nفي ديني ودنياي وأهلي ومالي",
    "🌙 <b>اللهم عافني في بدني</b>\nاللهم عافني في سمعي، اللهم عافني في بصري",
    "🌙 <b>أمسينا على فطرة الإسلام</b>\nوكلمة الإخلاص ودين نبينا محمد ﷺ",
    "🌙 <b>سبحان الله وبحمده</b>\nعدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته",
    "🌙 <b>اللهم صل وسلم على نبينا محمد</b>\nوعلى آله وصحبه أجمعين",
]

DUA_LIST = [
    "🤲 <b>دعاء الخروج من المنزل:</b>\nبسم الله، توكلت على الله، ولا حول ولا قوة إلا بالله",
    "🤲 <b>دعاء الدخول إلى المنزل:</b>\nبسم الله ولجنا، وبسم الله خرجنا، وعلى ربنا توكلنا",
    "🤲 <b>دعاء قبل النوم:</b>\nباسمك اللهم أموت وأحيا",
    "🤲 <b>دعاء الاستيقاظ:</b>\nالحمد لله الذي أحيانا بعد ما أماتنا وإليه النشور",
    "🤲 <b>دعاء قبل الأكل:</b>\nبسم الله، اللهم بارك لنا فيما رزقتنا وقنا عذاب النار",
    "🤲 <b>دعاء بعد الأكل:</b>\nالحمد لله الذي أطعمني هذا ورزقنيه من غير حول مني ولا قوة",
    "🤲 <b>دعاء الدخول إلى المسجد:</b>\nاللهم افتح لي أبواب رحمتك",
    "🤲 <b>دعاء الخروج من المسجد:</b>\nاللهم إني أسألك من فضلك",
    "🤲 <b>دعاء الهم والحزن:</b>\nاللهم إني عبدك، ابن عبدك، ابن أمتك، ناصيتي بيدك، ماض في حكمك، عدل في قضاؤك",
    "🤲 <b>دعاء القلق:</b>\nاللهم إني أعوذ بك من الهم والحزن والعجز والكسل",
    "🤲 <b>دعاء المطر:</b>\nاللهم صيباً نافعاً، اللهم صيباً هنيئاً",
    "🤲 <b>دعاء الرعد:</b>\nسبحان الذي يسبح الرعد بحمده والملائكة من خيفته",
    "🤲 <b>دعاء السفر:</b>\nاللهم هون علينا سفرنا هذا واطو عنا بعده، اللهم أنت الصاحب في السفر",
    "🤲 <b>دعاء العطاس:</b>\nالحمد لله",
    "🤲 <b>دعاء رد العطاس:</b>\nيرحمك الله",
]


def PrivateReligiousRouter() -> Router:
    router = Router(name="private_religious")

    @router.callback_query(F.data == "rel_quran")
    async def show_quran(cq: CallbackQuery):
        await cq.answer()
        keyboard = []
        row = []
        for i, name in enumerate(SURAH_NAMES, 1):
            row.append(InlineKeyboardButton(text=name, callback_data=f"quran_{i}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="section_religious")])

        await cq.message.edit_text(
            "📖 <b>القرآن الكريم</b>\n"
            "━━━━━━━━━━━━━━\n"
            "✨ اختر السورة لقراءتها:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    @router.callback_query(F.data.startswith("quran_"))
    async def read_surah(cq: CallbackQuery):
        await cq.answer()
        surah_num = cq.data.split("_")[1]
        idx = int(surah_num) - 1
        surah_name = SURAH_NAMES[idx] if 0 <= idx < len(SURAH_NAMES) else "الفاتحة"
        await cq.message.edit_text(
            f"📖 <b>سورة {surah_name}</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🌙 <b>سورة رقم {surah_num}</b>\n"
            f"📖 من القرآن الكريم\n\n"
            f"📖 <a href='https://quran.com/{surah_num}'>اقرأ سورة {surah_name} كاملة</a>\n\n"
            f"🎧 <a href='https://quran.com/{surah_num}'>استمع لتلاوة السورة</a>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📖 القراءة", url=f"https://quran.com/{surah_num}")],
                [InlineKeyboardButton(text="🎧 استماع", url=f"https://quran.com/{surah_num}")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="rel_quran")],
            ]),
            disable_web_page_preview=True
        )

    @router.callback_query(F.data == "rel_adhkar")
    async def show_adhkar(cq: CallbackQuery):
        await cq.answer()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌅 أذكار الصباح", callback_data="adhkar_morning")],
            [InlineKeyboardButton(text="🌇 أذكار المساء", callback_data="adhkar_evening")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_religious")],
        ])
        await cq.message.edit_text(
            "📿 <b>الأذكار اليومية</b>\n"
            "━━━━━━━━━━━━━━\n"
            "اختر نوع الذكر:",
            reply_markup=keyboard
        )

    @router.callback_query(F.data == "adhkar_morning")
    async def show_morning(cq: CallbackQuery):
        await cq.answer()
        txt = "🌅 <b>أذكار الصباح</b>\n━━━━━━━━━━━━━━━━━\n\n"
        for i, dhikr in enumerate(ADHKAR_MORNING, 1):
            txt += f"{i}. {dhikr}\n\n"
        await cq.message.edit_text(
            txt,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="rel_adhkar")]
            ])
        )

    @router.callback_query(F.data == "adhkar_evening")
    async def show_evening(cq: CallbackQuery):
        await cq.answer()
        txt = "🌇 <b>أذكار المساء</b>\n━━━━━━━━━━━━━━━━━\n\n"
        for i, dhikr in enumerate(ADHKAR_EVENING, 1):
            txt += f"{i}. {dhikr}\n\n"
        await cq.message.edit_text(
            txt,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="rel_adhkar")]
            ])
        )

    @router.callback_query(F.data == "rel_dua")
    async def show_dua(cq: CallbackQuery):
        await cq.answer()
        dua = random.choice(DUA_LIST)
        await cq.message.edit_text(
            dua,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 دعاء آخر", callback_data="rel_dua")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_religious")],
            ])
        )

    return router
