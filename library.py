import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


def library_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💡 معلومات عامة", callback_data="lib_facts")],
        [InlineKeyboardButton(text="📝 اقتباسات", callback_data="lib_quotes")],
        [InlineKeyboardButton(text="📚 كتب PDF", callback_data="lib_books")],
        [InlineKeyboardButton(text="🔙 العودة", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


FACTS = [
    "🧠 <b>هل تعلم؟</b> النحل يرقص عندما يجد رحيقاً ليخبر النحلات الأخرى! 🐝",
    "🧠 <b>هل تعلم؟</b> الأخطبوط لديه 3 قلوب! ❤️❤️❤️",
    "🧠 <b>هل تعلم؟</b> الفراشة تتذوق الطعام بأرجلها! 🦋",
    "🧠 <b>هل تعلم؟</b> الضحك يحرق سعرات حرارية! 😂",
    "🧠 <b>هل تعلم؟</b> قلب الإنسان ينبض 100 ألف مرة في اليوم! 💓",
    "🧠 <b>هل تعلم؟</b> الأسماك تتواصل عن طريق إطلاق الغازات! 🐟",
    "🧠 <b>هل تعلم؟</b> القمر يبتعد عن الأرض 3.8 سم كل عام! 🌙",
    "🧠 <b>هل تعلم؟</b> العسل لا يفسد أبداً! 🍯",
    "🧠 <b>هل تعلم؟</b> الزرافة تستطيع تنظيف أذنيها بلسانها! 🦒",
    "🧠 <b>هل تعلم؟</b> الكسلان يستطيع حبس أنفاسه تحت الماء لمدة 40 دقيقة! 🦥",
    "🧠 <b>هل تعلم؟</b> الفيل هو الحيوان الوحيد الذي لا يستطيع القفز! 🐘",
    "🧠 <b>هل تعلم؟</b> الثلج ليس أبيضاً بل شفافاً! ❄️",
    "🧠 <b>هل تعلم؟</b> قوس قزح دائري وليس نصف دائرة! 🌈",
    "🧠 <b>هل تعلم؟</b> القطط لا تستطيع تذوق الحلويات! 🐱",
    "🧠 <b>هل تعلم؟</b> البرتقال ليس برتقالياً في المناطق الحارة! 🍊",
    "🧠 <b>هل تعلم؟</b> أنت أطول في الصباح منه في المساء! 📏",
    "🧠 <b>هل تعلم؟</b> عظام الإنسان أقوى من الخرسانة! 💪",
    "🧠 <b>هل تعلم؟</b> النمل لا ينام أبداً! 🐜",
    "🧠 <b>هل تعلم؟</b> الدببة القطبية جلدها أسود وليس أبيض! 🐻‍❄️",
    "🧠 <b>هل تعلم؟</b> الأناناس يحتاج 3 سنوات لينضج! 🍍",
    "🧠 <b>هل تعلم؟</b> لسان الحوت الأزرق يزن وزن فيل! 🐋",
    "🧠 <b>هل تعلم؟</b> أسرع مخلوق على الأرض هو الصقر! 🦅",
    "🧠 <b>هل تعلم؟</b> التمساح لا يستطيع إخراج لسانه! 🐊",
    "🧠 <b>هل تعلم؟</b> النعامة عيونها أكبر من دماغها! 👀",
    "🧠 <b>هل تعلم؟</b> الإنسان البالغ لديه 206 عظمة! 🦴",
    "🧠 <b>هل تعلم؟</b> أقوى عضلة في الجسم هي اللسان! 👅",
    "🧠 <b>هل تعلم؟</b> الرئة اليمنى تستوعب هواء أكثر من اليسرى! 💨",
    "🧠 <b>هل تعلم؟</b> الكبد هو العضو الوحيد الذي يمكنه التجدد! 🫁",
    "🧠 <b>هل تعلم؟</b> العطس يخرج بسرعة 160 كم/ساعة! 🤧",
    "🧠 <b>هل تعلم؟</b> أظافر اليد تنمو أسرع من أظافر القدم! 💅",
    "🧠 <b>هل تعلم؟</b> الجلد هو أكبر عضو في جسم الإنسان! 🧑",
    "🧠 <b>هل تعلم؟</b> يمكن للإنسان البقاء بدون طعام شهر لكن بدون ماء أسبوع! 💧",
    "🧠 <b>هل تعلم؟</b> النوم يطهر الدماغ من السموم! 😴",
    "🧠 <b>هل تعلم؟</b> التثاؤب يبرد الدماغ! 🥱",
    "🧠 <b>هل تعلم؟</b>警 زبد البحر يستخدم في صنع مستحضرات التجميل! 🌊",
    "🧠 <b>هل تعلم؟</b> الذهب الخالص 24 قيراطاً! 🥇",
    "🧠 <b>هل تعلم؟</b> الألماس يتكون من الكربون فقط! 💎",
    "🧠 <b>هل تعلم؟</b> أقصر حرب في التاريخ كانت 38 دقيقة! ⚔️",
    "🧠 <b>هل تعلم؟</b> أول طابع بريد كان في بريطانيا 1840! 📮",
    "🧠 <b>هل تعلم؟</b> الكوكاكولا كانت تحتوي على الكوكايين! 🥤",
    "🧠 <b>هل تعلم؟</b> الشوكولاتة كانت تستخدم كنقود في حضارة المايا! 🍫",
    "🧠 <b>هل تعلم؟</b> الموز غني بالبوتاسيوم المفيد للقلب! 🍌",
    "🧠 <b>هل تعلم؟</b> البطاطس تحتوي على فيتامين C! 🥔",
    "🧠 <b>هل تعلم؟</b> الكافيين يحتاج 6 ساعات لمغادرة الجسم! ☕",
    "🧠 <b>هل تعلم؟</b> الضفدع لا يشرب الماء بل يمتصه من جلده! 🐸",
    "🧠 <b>هل تعلم؟</b> الحلزون يستطيع النوم 3 سنوات! 🐌",
    "🧠 <b>هل تعلم؟</b> هناك أنواع من الأسماك تستطيع العيش خارج الماء! 🐠",
    "🧠 <b>هل تعلم؟</b> الزرافة لديها نفس عدد فقرات الرقبة مثل الإنسان! 🦒",
    "🧠 <b>هل تعلم؟</b> الدلفين ينام بعين واحدة مفتوحة! 🐬",
    "🧠 <b>هل تعلم؟</b> الفأر يمكنه العيش بدون ماء أطول من الجمل! 🐭",
    "🧠 <b>هل تعلم؟</b> عدد سكان الأرض يتزايد بمقدار 200 ألف شخص يومياً! 🌍",
    "🧠 <b>هل تعلم؟</b> أعلى جبل في العالم هو إيفرست (8848م)! 🏔️",
    "🧠 <b>هل تعلم؟</b> أعمق نقطة في المحيط هي خندق ماريانا (11كم)! 🌊",
    "🧠 <b>هل تعلم؟</b> صحراء الربع الخالي هي أكبر صحراء رملية! 🏜️",
    "🧠 <b>هل تعلم؟</b> نهر النيل هو أطول نهر في العالم! 🌊",
    "🧠 <b>هل تعلم؟</b> الأقصر تحتوي على ثلث آثار العالم! 🏛️",
]

QUOTES = [
    "📝 <b>اقتباس:</b>\n\"على قدر أهل العزم تأتي العزائم\" - المتنبي",
    "📝 <b>اقتباس:</b>\n\"إذا ضاقت بك الدنيا فلا تقل يارب عندي هم كبير بل قل: يا هم لي رب كبير\"",
    "📝 <b>اقتباس:</b>\n\"لا تحسبن المجد تمراً أنت آكله، لن تبلغ المجد حتى تلعق الصبرا\"",
    "📝 <b>اقتباس:</b>\n\"إن السماء ترجى حين تحتجب، والماء يرجى حين يحتبس\"",
    "📝 <b>اقتباس:</b>\n\"وما نيل المطالب بالتمني، ولكن تؤخذ الدنيا غلابا\"",
    "📝 <b>اقتباس:</b>\n\"من جد وجد، ومن زرع حصد\"",
    "📝 <b>اقتباس:</b>\n\"لكل مجتهد نصيب\"",
    "📝 <b>اقتباس:</b>\n\"الصبر مفتاح الفرج\"",
    "📝 <b>اقتباس:</b>\n\"من طلب العلا سهر الليالي\"",
    "📝 <b>اقتباس:</b>\n\"رحم الله امرأ عرف قدر نفسه\"",
    "📝 <b>اقتباس:</b>\n\"خير الكلام ما قل ودل\"",
    "📝 <b>اقتباس:</b>\n\"إن مع العسر يسراً\"",
    "📝 <b>اقتباس:</b>\n\"لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه\"",
    "📝 <b>اقتباس:</b>\n\"الكلمة الطيبة صدقة\"",
    "📝 <b>اقتباس:</b>\n\"تبسمك في وجه أخيك صدقة\"",
    "📝 <b>اقتباس:</b>\n\"ليس الفتى من قال كان أبي، لكن الفتى من قال ها أنا ذا\"",
    "📝 <b>اقتباس:</b>\n\"إذا كنت ذا رأي فكن ذا تدبر، فإن فساد الرأي أن تتبعه\"",
    "📝 <b>اقتباس:</b>\n\"لا تنه عن خلق وتأتي مثله، عار عليك إذا فعلت عظيم\"",
    "📝 <b>اقتباس:</b>\n\"كل ابن آدم خطاء، وخير الخطائين التوابون\"",
    "📝 <b>اقتباس:</b>\n\"إنما الدنيا ثلاثة: يوم مضى لن يعود، ويوم أنت فيه لن يدوم، ويوم غد لا تدري أأنت فيه أم لا\"",
    "📝 <b>اقتباس:</b>\n\"الدنيا ساعة فاجعلها طاعة\"",
    "📝 <b>اقتباس:</b>\n\"لا خير في كثير من نجواهم إلا من أمر بصدقة أو معروف أو إصلاح بين الناس\"",
    "📝 <b>اقتباس:</b>\n\"واعف عن الناس فالناس أكفاء، فالناس للناس منذ البدء أعداء\"",
    "📝 <b>اقتباس:</b>\n\"تعلموا العلم فإنه زين لأهله\"",
    "📝 <b>اقتباس:</b>\n\"اللهم إني أسألك علماً نافعاً ورزقاً طيباً وعملاً متقبلاً\"",
]

BOOKS = [
    {"title": "الأب الغني والأب الفقير", "author": "روبرت كيوساكي", "url": "https://drive.google.com/your-book-link-1"},
    {"title": "العادات السبع للناس الأكثر فعالية", "author": "ستيفن كوفي", "url": "https://drive.google.com/your-book-link-2"},
    {"title": "فكر وازدد ثراءً", "author": "نابليون هيل", "url": "https://drive.google.com/your-book-link-3"},
    {"title": "قوة العادات", "author": "تشارلز دويج", "url": "https://drive.google.com/your-book-link-4"},
    {"title": "الرجال من المريخ والنساء من الزهرة", "author": "جون غراي", "url": "https://drive.google.com/your-book-link-5"},
    {"title": "ايكيغاي", "author": "هيكتور غارسيا", "url": "https://drive.google.com/your-book-link-6"},
    {"title": "قواعد السطوة", "author": "روبرت غرين", "url": "https://drive.google.com/your-book-link-7"},
    {"title": "فن اللامبالاة", "author": "مارك مانسون", "url": "https://drive.google.com/your-book-link-8"},
    {"title": "الخيميائي", "author": "باولو كويلو", "url": "https://drive.google.com/your-book-link-9"},
    {"title": "نظرية الفستق", "author": "فهد عامر الأحمدي", "url": "https://drive.google.com/your-book-link-10"},
]


def PrivateLibraryRouter() -> Router:
    router = Router(name="private_library")

    @router.callback_query(F.data == "lib_facts")
    async def show_fact(cq: CallbackQuery):
        await cq.answer()
        fact = random.choice(FACTS)
        await cq.message.edit_text(
            fact,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 معلومة أخرى", callback_data="lib_facts")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_library")],
            ])
        )

    @router.callback_query(F.data == "lib_quotes")
    async def show_quote(cq: CallbackQuery):
        await cq.answer()
        quote = random.choice(QUOTES)
        await cq.message.edit_text(
            quote,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 اقتباس آخر", callback_data="lib_quotes")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_library")],
            ])
        )

    @router.callback_query(F.data == "lib_books")
    async def show_books(cq: CallbackQuery):
        await cq.answer()
        txt = "📚 <b>الكتب المتوفرة</b>\n━━━━━━━━━━━━━━\n\n"
        keyboard = []
        for i, book in enumerate(BOOKS, 1):
            txt += f"{i}. <b>{book['title']}</b> - {book['author']}\n"
            keyboard.append([InlineKeyboardButton(
                text=f"📖 {book['title'][:30]}",
                callback_data=f"book_{i}"
            )])
        keyboard.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="section_library")])

        await cq.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    @router.callback_query(F.data.startswith("book_"))
    async def show_book(cq: CallbackQuery):
        await cq.answer()
        idx = int(cq.data.split("_")[1]) - 1
        if 0 <= idx < len(BOOKS):
            book = BOOKS[idx]
            await cq.message.edit_text(
                f"📖 <b>{book['title']}</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"✍️ المؤلف: <b>{book['author']}</b>\n\n"
                f"📥 <a href='{book['url']}'>اضغط هنا لتحميل الكتاب</a>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📥 تحميل", url=book['url'])],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="lib_books")],
                ]),
                disable_web_page_preview=True
            )

    return router
