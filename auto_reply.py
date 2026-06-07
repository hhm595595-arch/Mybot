import random

from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

from database import db
from utils.helpers import norm, is_admin

AUTO_REPLIES = {
    # ── Greetings (تحيات) ──
    "السلام عليكم": [
        "وعليكم السلام ورحمة الله وبركاته.. نورتنا بطلتك البهية 🤍✨",
        "يا ميت أهلاً وسهلاً.. وعليكم السلام والرحمة 🌹",
        "وعليكم السلام.. الجروب نور بدخولك يا غالي 👑",
        "وعليكم السلام ورحمة الله.. أسعد الله أوقاتك بكل خير 🌸"
    ],
    "سلام عليكم": [
        "وعليكم السلام يا رفيق الدرب 🕊️🌸",
        "يا هلا ومرحبا وعليكم السلام 🤍✨"
    ],
    "صباح الخير": [
        "صباحك سكر ومسك وعنبر.. نهارك سعيد ☀️🌹",
        "صباح النور والسرور.. والورد المنثور 🌸✨",
        "صباحك جميل كجمال روحك.. أهلاً بك 🌅"
    ],
    "مساء الخير": [
        "مساء الورد والياسمين على الناس الطيبين 🌆🤍",
        "مساءك حلاوة وسعادة لا تنتهي 🌟",
        "مساء الأنوار والمسرات 🌺"
    ],
    "هلا": [
        "يا هلا وغلا ومية كرتون حلا 🍬✨",
        "هلا بك نورت الجروب والله 🌟",
        "أهلاً بالشخص المميز، هلا فيك 👑"
    ],
    "هاي": "😊 هاي، كيفك؟",
    "هاي": "👋 هلا والله",
    "hello": "👋 <b>Hello!</b> How are you? 🌸",
    "hi": "👋 <b>Hi there!</b> 🤍",
    "hey": "🌟 Hey! How's it going? 😊",
    "good morning": "☀️ <b>Good Morning!</b> Have a blessed day 🌸",
    "good evening": "🌆 <b>Good Evening!</b> Hope you had a great day 🌙",

    # ── Islamic (إسلاميات) ──
    "الحمد لله": "🤲 <b>الحمد لله على كل حال</b>",
    "الحمدلله": "🤍 <b>الحمد لله رب العالمين</b>",
    "لا اله الا الله": "🌙 <b>لا إله إلا الله محمد رسول الله</b> 🕋",
    "سبحان الله": "🤲 <b>سبحان الله وبحمده</b>\nسبحان الله العظيم",
    "الله اكبر": "🌟 <b>الله أكبر كبيراً</b> والحمد لله كثيراً",
    "استغفر الله": "🤍 <b>أستغفر الله العظيم</b> وأتوب إليه",
    "ما شاء الله": "🌸 <b>ما شاء الله تبارك الرحمن</b>",
    "بسم الله": "🤲 <b>بسم الله الرحمن الرحيم</b>",
    "ان شاء الله": "🤍 <b>إن شاء الله</b> تعالى",
    "انشاء الله": "🤍 إن شاء الله 🤍",
    "بارك الله": "🤍 <b>بارك الله فيك</b> وجزاك كل خير",
    "بارك الله فيك": "🤍 وفيك بارك الله",
    "جزاك الله": "🤲 <b>وجزاكم الله خيراً</b>",
    "جزاك الله خيرا": "🤲 واياك يارب",
    "اللهم": "🤲 <b>اللهم آمين</b> 🤲",
    "اللهم امين": "🤲 <b>اللهم آمين جميعاً</b> 🤲",
    "اللهم آمين": "🤲 آمين يارب العالمين 🤲",
    "صلى الله": "🌸 <b>صلى الله على سيدنا محمد</b> ﷺ",
    "عليه الصلاة": "🌙 صلى الله عليه وسلم 🤍",
    "عليه الصلاة والسلام": "🌙 صلى الله عليه وسلم تسليماً كثيراً",
    "محمد": "ﷺ صلى الله عليه وسلم 🌸",
    "رسول الله": "ﷺ صلى الله عليه وسلم 🤍",
    "الفاتحة": "📖 <b>بسم الله الرحمن الرحيم</b>\nالحمد لله رب العالمين 🤍",
    "ادعيلنا": "🤲 <b>اللهم اغفر لنا وارحمنا</b>\n🤲 اللهم ارزقنا الجنة 🤍",
    "ادعولي": "🤲 ربنا يوفقك ويسعدك 🤍",

    # ── Thanks (شكر) ──
    "شكرا": "🌸 <b>العفو</b>، تحت أمرك دائماً 🤍",
    "شكراً": "🌹 <b>العفو</b>، هذا أقل واجب",
    "تسلم": "🤍 <b>تسلم لي</b> يا غالي",
    "تسلم ايدك": "🤍 <b>الله يسلمك</b> يا رب",
    "تسلملي": "🤍 تسلملي انت",
    "مشكور": "🌸 <b>العفو</b>، الله يسعدك",
    "ثانكس": "🌹 <b>Welcome</b>, anytime!",
    "thanks": "🤍 <b>You're welcome</b> 🤍",
    "thank you": "🌸 You're very welcome!",
    "thx": "🌸 Anytime!",
    "ty": "🤍 You're welcome!",

    # ── Love / Friendship (حب وصداقة) ──
    "احبك": "😂😂 <b>يلا بينا</b> يخربيت الحب",
    "بحبك": "😹 <b>احا</b> 😹😹 يلا بينا",
    "بحبك يا": "😹😹 يلا يسطا",
    "حبيبي": "🌹 <b>حبيبي نورت والله</b> 🤍",
    "حبيبتي": "🌸 <b>🤍</b> يخربيت الرومانسية",
    "قلبي": "🌹 <b>قلبي نورت</b> 🤍",
    "روحي": "🌸 <b>روحي انت</b> 🤍",
    "عيوني": "🤍 <b>عيوني</b> والله",
    "عمري": "❤️ <b>عمري</b> كله",
    "مشتاق": "😢 <b>مشتاق كمان</b> 🤍💔",
    "اشتقت": "😢 <b>اشتقت الك</b> 💔",
    "اشتقتلك": "😢💔 وحشتني كتير",
    "وحشتني": "😢🤍 <b>وحشتني كتير</b> والله",
    "مشتاقلك": "😢💔 <b>مشتاقلك والله</b> 💔",
    "بموت فيك": "😂😂 <b>يلا يسطا</b> 😹",
    "حبيب قلبي": "😹😹😹 <b>خلينا في حالنا</b>",
    "حياة": "🌸 حياتي كلها 🤍",
    "عشق": "❤️ عشق 🤍",
    "miss you": "🤍 <b>Miss you too</b> 🤍",
    "i love you": "❤️ Love you too! 🌸",

    # ── Laugh / Fun (ضحك وفرفشة) ──
    "هههه": "😂😂😂 <b>هههه</b>",
    "ههههه": "😹😹😹 يخربيت الضحك",
    "😂": "😹😹😹",
    "😭": "😭😭😭 <b>بتوجع</b> 😭",
    "😹": "😂😂😂🐱",
    "لول": "😂😂 <b>لول</b>",
    "lol": "😂😂 <b>lol</b>",
    "haha": "😂😂 <b>haha</b>",
    "😂😂": "😹😹😹 <b>الله يضحك سنك</b>",
    "😂😂😂": "😹😹😹",
    "هه": "😂 هه",
    "ههه": "😂😂",

    # ── Chat / Daily (شات ويوميات) ──
    "كيفك": "😊 <b>تمام الحمد لله</b>\nوانت كيفك؟ 🌸",
    "كيف الحال": "🌸 <b>تمام يا غالي</b>\nانت اخبارك؟",
    "عامل ايه": "😂 <b>عامل ايه معاك الحلاوة</b>",
    "عامل اي": "🌹 <b>الحمد لله</b> تمام",
    "اخبارك": "😊 <b>اخبارك معاك النشاط</b>\nانت اخبارك؟",
    "اخبار": "🌸 اخبارك عاملة ايه؟",
    "في ايه": "🌹 <b>في ايه منور والله</b>",
    "مالك": "😂 <b>مالك يلا خير</b>",
    "مالك يلا": "😂😂 مالك يلا",
    "تعال": "🌸 <b>تعال تحت أمرك</b> 🤍",
    "تعالي": "🌹 <b>تعالي</b> تحت أمرك",
    "طيب": "🌸 <b>طيب</b> 🤍",
    "تم": "✅ <b>تم</b> 👍",
    "اوكي": "👍 <b>أوكي</b> ✅",
    "ok": "👍 <b>OK</b> ✅",
    "تمام": "🌸 <b>تمام</b> الحمد لله",
    "ماشي": "🚶 <b>ماشي</b> الحال",
    "موافق": "👍 <b>موافق</b> ✅",
    "نعم": "🌸 <b>نعم</b> 🌸",
    "ايوا": "👍 <b>ايوا</b> 😂",
    "اه": "🌸 اه",
    "لا": "❌ \u0644\u0627",
    "معليش": "🌸 <b>معليش</b> عادي",

    # ── Goodbye (وداع) ──
    "مع السلامة": "🌸 <b>مع السلامة</b> الله يسلمك 🤍",
    "باي": "🌹 <b>باي باي</b> 🤍",
    "باي باي": "🌸 باي، نورت والله",
    "bye": "🤍 <b>Bye bye</b> take care 🌸",
    "goodbye": "🌸 <b>Goodbye</b> see you soon 🤍",
    "see you": "👋 See you later! 🤍",
    "تصبح على خير": "🌙 <b>وانت من أهله</b> 🤍",
    "تصبح": "🌙 تصبح على خير 🤍",
    "نشوفك": "🌸 نشوفك على خير",

    # ── Important / Serious (مهم) ──
    "انتبه": "🤍 <b>انتبه على نفسك</b> 🫶",
    "انتبهي": "🌸 انتبهي على نفسك 🤍",
    "حذاري": "⚠️ <b>حذاري ثم حذاري</b>",
    "ممنوع": "🚫 <b>ممنوع</b> ✅",
    "سم": "🤍 <b>اسم الله عليك</b> 🤍",
    "اسم الله": "🤍 <b>اسم الله عليك</b> يخربيت العين",
    "الله معك": "🤲 الله معك 🤍",
    "الله يوفقك": "🤲 آمين جميعاً 🤍",
    "ربنا يوفقك": "🤲 ربنا يوفقك ويسعدك",
    "ربنا معاك": "🤲 ربنا معاك 🤍",
    "حظ سعيد": "🍀 <b>حظ سعيد</b> يا رب",
    "بالتوفيق": "🌟 <b>بالتوفيق</b> يا رب 🤍",
    "مبروك": "🎉 <b>مبروك</b> 🥳🎊",
    "الف مبروك": "🎉🎉 <b>ألف مبروك</b> 🎊🥳",
    "الله يرحمه": "🤲 <b>الله يرحمه</b> ويغفر له 🤍",
    "البقرة": "🤲 <b>إنا لله وإنا إليه راجعون</b> 🤍",
    "عظم الله اجركم": "🤲 عظم الله اجركم 🤍",

    # ── Fun / Joking (مزح) ──
    "نوم": "😴 <b>نوم العوافي</b> 😂",
    "نايم": "😂 <b>نايم صح النوم</b> 😴",
    "اكل": "🍔 <b>هاته</b> 😂😂",
    "كل": "🍕 <b>كلي</b> 😂😂",
    "جوعان": "🍝 <b>جوعان تعال كل</b> 😂",
    "عطشان": "🥤 <b>اشرب ماي</b> 😂",
    "قهوة": "☕️ <b>قهوة الصباح</b> ☕️🌅",
    "شاي": "🍵 <b>شاي العصر</b> 🍵🌇",
    "نسكافيه": "☕ نسكافيه 😂",
    "فطار": "🥞 <b>فطور</b> بالهناء والشفاء 🌸",
    "غدا": "🍲 <b>غدا</b> بالهناء 🌸",
    "عشا": "🥘 <b>عشا</b> هنيئاً مريئاً 🌸",
    "نرجس": "😂😂 <b>نرجس</b> 😂😂",
    "مزاج": "🌸 <b>مزاجك ايه النهارده؟</b>",
    "زي الفل": "🌹 <b>زي الفل يا باشا</b>",
    "نورت": "🌸 <b>نورت والله</b> 🤍",
    "منور": "🌹 <b>منور بحضورك</b> 🤍",
    "نورتوا": "🌸 نورتوا والله",
    "حاضر": "👍 حاضر 🙋",
    "تمام التمام": "💯 تمام يا كبير",
    "جامد": "🔥 <b>جامد</b> والله",
    "جمدان": "🔥 <b>جمدان</b> 😂",
    "فشيخ": "🔥 فشيخ يسطا",
    "متألق": "✨ <b>متألق</b> كالعادة",
    "شاطر": "🌟 <b>شاطر</b> يستاهل 🏅",
    "زلمة": "💪 <b>زلمة</b> والله",
    "حكاية": "🌟 <b>حكاية</b> والله 😎",
    "نار": "🔥🔥 <b>نار</b> يابا",
    "نمبر وان": "🥇 <b>نمبر وان</b> 🌟",

    # ── Game (ألعاب وتسلية) ──
    "يلا": "🌸 <b>يلا بينا</b> 🤍",
    "يلا بينا": "😂 <b>يلا بينا نتحرك</b>",
    "كوم": "😂 <b>كوم يلا</b>",
    "game": "🎮 <b>Game on!</b> 🎮",
    "لعبة": "😂🎮 <b>لعبة</b> يلا بينا",
    "بص": "👀 بص",
    "شوف": "👀 شوف",
    "طز": "😐 طز 😂",
    "خلاص": "✅ خلاص تم",

    # ── Compliments (مجاملات) ──
    "انت جميل": "🌹 انت الأجمل 🤍",
    "انت حلو": "😊 انت الأحلى 🌸",
    "انت كيوت": "🥹 انت الكيوت 🤍",
    "جميل": "🌸 <b>جميل</b> والله",
    "حلو": "😊 <b>حلو</b> الكلام الحلو 🌸",
    "رائع": "🌟 <b>رائع</b> انت 🌟",
    "ذكي": "🧠 <b>ذكي</b> يستاهل النجمه 🌟",
    "عبقري": "🧠💡 <b>عبقري</b> زمانك",
    "وسيم": "😎 <b>وسيم</b> 😎",
    "قمر": "🌙 <b>قمر</b> 🤍",
    "يا قمر": "🌙 نورت 🤍",
    "يا عسل": "🍯 <b>عسل</b> انت 🤍",
    "تحفة": "🏆 <b>تحفة</b> والله",
    "ده غير": "😱🔥 ده غير",
    "عظمة": "👑 <b>عظمة</b> على عظمة",
    "نكتة": [
        "مرة واحد غبي راح للدكتور، قاله يا دكتور أنا كل ما أنام أحلم بحمير بيلعبوا كورة، الدكتور قاله ماتنمش النهاردة، قاله ماقدرش ده النهاردة النهائي 😂",
        "نملة تزوجت فيل، الفيل مات، النملة قضت عمرها تحفر له قبر 😹",
        "غبي وقع في الحفرة، نزلوله حبل، طلع عشان يجيب مقص ويقص الحبل 😹",
        "واحد مسطول بيسأل صاحبه: هو يوم الخميس يوافق كام في الشهر؟ قاله معرفش يمكن 15، قاله ياااه يعني يوم الثلاثاء! 😂",
    ],
    "نكت": [
        "مرة مدرس سأل طالب: ليه القلب بيدق؟ قاله عشان الرقصة تبدأ 😹",
        "مرة واحد محشش بيسأل واحد: الساعة كام؟ قاله عشرة وعشرة.. قاله ماتقول عشرين وتخلص! 😂",
    ],
    "اقتباس": [
        "💡 «لا تكن أسهل ما في الحياة، ولا أصعب ما فيها، بل كن أنت الحياة.»",
        "🌟 «النجاح ليس النهاية، والفشل ليس قاتلًا؛ إنما الشجاعة للاستمرار هي ما يهم.»",
        "✨ «ما تبحث عنه يبحث عنك.»",
        "🌱 «لا تتوقف عندما تتعب، توقف عندما تنتهي.»",
    ],
    "حكمة": [
        "📜 «من سار على الدرب وصل، ومن زرع حصد.»",
        "📜 «لا تؤجل عمل اليوم إلى الغد.»",
        "📜 «العقل السليم في الجسم السليم.»",
    ],
    "خاص": "🚫 <b>ممنوع الخاص يا عسل!</b> التزم بالجروب أحسن لك 😡🔪",
    "تعال خاص": "🚫 <b>لا يوجد خاص هنا!</b> كل شيء على المكشوف في الجروب 😎✨",
    "تعالي خاص": "🚫 <b>ممنوع الخاص يا وحش!</b> عيب كذا احترم نفسك 🔪",
    "خاصك": "🚫 <b>ممنوع الخاص يا حبيبي!</b> 😡",
}

SINGLE_CHAR_REPLIES = {
    "ا": [
        "ايه يا غالي نورت 🌸",
        "اطلب وتمنى يا سيدي 🤍",
        "ايه الحلاوة دي كلها! ✨",
        "اقولك حكمة؟ «من جد وجد» 📚"
    ],
    "ب": "باي باي، نشوفك على خير 👋",
    "ج": "جميل حضورك في الجروب والله 😊",
    "ح": "حبيبي انت والله، نورت 🌹",
    "خ": "خير إن شاء الله، مالك؟ 😂",
    "د": "دوم الضحكة والوناسة يارب 🤍",
    "ذ": "ذوقك راقي يا نجم 🌟",
    "ر": "رايق انت اليوم 🌸",
    "ز": "زين ما سويت والله 🌹",
    "س": "سلام مربع للجدعان 🌹",
    "ش": [
        "شو فيك؟ 😂",
        "شاطر والله 🌟",
        "شو اخبارك يا وردة؟ 🌸"
    ],
    "ص": "صباح الفل والياسمين ☀️",
    "ض": "ضيق؟ افردها وروق 😂",
    "ط": "طبعا طبعا، انت معلم 😊",
    "ظ": "ظريف كعادتك 😂",
    "ع": "عيوني لك يا غالي 🌹",
    "غ": "غالي والطلب رخيص 🤍",
    "ف": "فينك مختفي؟ اشتقنالك 😂",
    "ق": "قول يا قلبي سامعك 😂",
    "ك": "كيفك يا حلو؟ 🌸",
    "ل": "لا اله الا الله محمد رسول الله 🕋",
    "م": [
        "مساء الورد 🌹",
        "منورنا والله ✨",
        "مستنيك من زمان 😂"
    ],
    "ن": "نعم يا عيوني 🌸",
    "ه": "هلا وغلا نورت 🌹",
    "و": "وحشتنا يا راجل 😂",
    "ي": "يلا بينا نولعها 🌸",
    "h": "Hey there! How are you doing? 🌸",
    "i": "I see you! Nice to have you here 😊",
    "k": "ok 👍",
    "m": "mmm 😂",
    "n": "no 🤍",
    "o": "oh 😂",
    "s": "sure 🌸",
    "w": "wow 😲",
    "x": "x 😂",
    "y": "yalla 😂",
    "z": "zzz 😴",
    "1": "واحد 🌸",
    "2": "اتنين 😂",
    "3": "تلاتة 🌹",
    "4": "اربعة 🤍",
    "5": "خمسة 😊",
    "6": "ستة 🌸",
    "7": "سبعة 🌸",
    "8": "تمانية 😂",
    "9": "تسعة 🌹",
    "10": "عشرة 🤍",
}


def GroupAutoReplyRouter() -> Router:
    router = Router(name="group_auto_reply")

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
    async def auto_reply_handler(msg: Message):
        try:
            print(f">>> [AUTO_REPLY_DEBUG] Received text: '{msg.text}' in chat {msg.chat.id}")
            if not msg.text:
                print(">>> [AUTO_REPLY_DEBUG] No text, returning")
                return
            user = msg.from_user
            if not user or user.is_bot:
                print(">>> [AUTO_REPLY_DEBUG] User is bot, returning")
                return

            chat_id = msg.chat.id

            is_active = await db.is_group_active(chat_id)
            print(f">>> [AUTO_REPLY_DEBUG] is_active: {is_active}")
            if not is_active:
                print(">>> [AUTO_REPLY_DEBUG] Group not active, returning")
                return

            text = msg.text.strip()
            text_norm = norm(text)
            text_raw = text_norm.replace(" ", "")
            lower = text.lower().strip()

            # ── Auto Reactions ──
            from aiogram.types import ReactionTypeEmoji
            if "مبروك" in lower or "الف مبروك" in lower:
                try: await msg.react([ReactionTypeEmoji(emoji="🎉")])
                except Exception: pass
            elif "حزين" in lower or "زعلان" in lower or "😢" in text:
                try: await msg.react([ReactionTypeEmoji(emoji="😢")])
                except Exception: pass
            elif "هههه" in lower or "😂" in text:
                try: await msg.react([ReactionTypeEmoji(emoji="😂")])
                except Exception: pass
            elif "نار" in lower or "🔥" in text:
                try: await msg.react([ReactionTypeEmoji(emoji="🔥")])
                except Exception: pass
            elif "حب" in lower or "قلبي" in lower or "❤️" in text:
                try: await msg.react([ReactionTypeEmoji(emoji="❤")])
                except Exception: pass

            auto_reply_enabled = await db.get_setting(chat_id, "auto_reply")
            print(f">>> [AUTO_REPLY_DEBUG] auto_reply_enabled: {auto_reply_enabled}")
            if auto_reply_enabled == 0:
                print(">>> [AUTO_REPLY_DEBUG] auto_reply disabled, returning")
                return

            print(f">>> [AUTO_REPLY_DEBUG] len(text_raw): {len(text_raw)}, in dict: {text_raw in SINGLE_CHAR_REPLIES}")
            if len(text_raw) == 1 and text_raw in SINGLE_CHAR_REPLIES:
                print(f">>> [AUTO_REPLY_DEBUG] Sending single char reply for {text_raw}")
                await msg.reply(SINGLE_CHAR_REPLIES[text_raw])
                return

            reply = AUTO_REPLIES.get(lower) or AUTO_REPLIES.get(text_norm) or AUTO_REPLIES.get(text_norm.replace(" ", ""))
            if reply:
                if isinstance(reply, list):
                    reply = random.choice(reply)
                await msg.reply(reply)
                return

            for key, reply_text in AUTO_REPLIES.items():
                if text_norm.startswith(key) and len(key) > 2:
                    if isinstance(reply_text, list):
                        reply_text = random.choice(reply_text)
                    await msg.reply(reply_text)
                    return

            important_keys = [
                "السلام عليكم", "الحمد لله", "لا اله الا الله",
                "سبحان الله", "الله اكبر", "استغفر الله", "ما شاء الله",
                "الحمدلله", "شكرا", "شكراً", "احبك", "بحبك", "حبيبي",
                "مشتاق", "وحشتني", "هههه",
            ]
            for key in important_keys:
                nkey = norm(key)
                if nkey in text_norm:
                    reply_text = AUTO_REPLIES.get(key) or AUTO_REPLIES.get(nkey)
                    if reply_text:
                        if isinstance(reply_text, list):
                            reply_text = random.choice(reply_text)
                        await msg.reply(reply_text)
                        return

            custom = await db.get_custom_replies(chat_id)
            for keyword, reply_text in custom.items():
                if keyword in lower or keyword in text_norm:
                    await msg.reply(f"💬 <b>{reply_text}</b>")
                    return

            # ── القوانين ──
            if lower in ("القوانين", "rules", "/rules"):
                rules = await db.get_rules(chat_id)
                if rules:
                    await msg.reply(f"📜 <b>قوانين الجروب</b>\n━━━━━━━━━━━━━━\n{rules}\n━━━━━━━━━━━━━━")
                else:
                    await msg.reply("📜 <b>لا توجد قوانين</b> محددة لهذا الجروب.")
                return

            # ── المشرفين ──
            if lower in ("المشرفين", "الادمن", "admins", "/admins"):
                try:
                    admins = await msg.chat.get_administrators()
                    lines = ["👮 <b>قائمة المشرفين</b>\n━━━━━━━━━━━━━━"]
                    for admin in admins:
                        role = "👑 المالك" if admin.status == ChatMemberStatus.CREATOR else "🔹 مشرف"
                        name = admin.user.full_name
                        uname = f" @{admin.user.username}" if admin.user.username else ""
                        lines.append(f"{role}: {name}{uname}")
                    lines.append("━━━━━━━━━━━━━━")
                    await msg.reply("\n".join(lines))
                except Exception:
                    await msg.reply("❌ لا يمكن جلب قائمة المشرفين.")
                return

            # ── معلومات الجروب ──
            if lower in ("معلومات", "معلومات الجروب", "groupinfo"):
                try:
                    admins = await msg.chat.get_administrators()
                    member_count = await msg.chat.get_member_count()
                    await msg.reply(
                        f"ℹ️ <b>معلومات الجروب</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"📛 الاسم: <b>{msg.chat.title}</b>\n"
                        f"🆔 الأيدي: <code>{chat_id}</code>\n"
                        f"👥 الأعضاء: <b>{member_count}</b>\n"
                        f"👮 المشرفين: <b>{len(admins)}</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━"
                    )
                except Exception:
                    await msg.reply("❌ لا يمكن جلب معلومات الجروب.")
                return

            # ── حسابي / معلوماتي ──
            if lower in ("حسابلي", "حسابي", "معلوماتي", "كشف", "/كشف"):
                from handlers.group.admin import show_user_info
                await show_user_info(msg, msg.chat, user)
                return

            # ── تفاعلي / رتبتي ──
            if lower in ("تفاعلي", "تفاعل", "رسائلي", "msg", "رتبتي", "رتبتك"):
                count = await db.get_messages_count(chat_id, user.id)
                bal = await db.get_balance(chat_id, user.id)
                warns = await db.get_warns(chat_id, user.id)
                rank = await db.get_custom_rank(chat_id, user.id)
                ranks_enabled = await db.get_setting(chat_id, "ranks_enabled")
                rank_display = f"🏅 الرتبة: <b>{rank}</b>\n" if (rank and ranks_enabled != 0) else ""
                
                await msg.reply(
                    f"📊 <b>إحصائياتك التفاعلية</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>{user.full_name}</b>\n"
                    f"🆔 <code>{user.id}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 رسائلك: <b>{count:,}</b>\n"
                    f"💰 رصيدك: <b>{bal:,}</b> نقطة\n"
                    f"⚠️ إنذاراتك: <b>{warns}</b>\n"
                    f"{rank_display}━━━━━━━━━━━━━━━━━━━"
                )
                return

            # ── الأوامر ──
            if lower in ("الاوامر", "الأوامر", "help", "/help"):
                await msg.reply(
                    "📋 <b>قائمة أوامر ريو 🚀</b>\n"
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    "👮 <b>أوامر المشرفين</b> (بالرد):\n"
                    "• <b>حظر</b> ─ حظر العضو\n"
                    "• <b>طرد</b> ─ طرد العضو\n"
                    "• <b>انذار</b> ─ إنذار\n"
                    "• <b>الغاء_انذار</b> ─ إلغاء إنذار\n"
                    "• <b>كتم</b> ─ كتم ساعة\n"
                    "• <b>الغاء_الكتم</b> ─ فك الكتم\n"
                    "• <b>كشف</b> ─ معلومات العضو\n"
                    "• <b>تثبيت</b> ─ تثبيت رسالة\n"
                    "• <b>تنظيف</b> ─ تنظيف الرسائل\n\n"
                    "📌 <b>أوامر عامة:</b>\n"
                    "• <b>القوانين</b> ─ عرض القوانين\n"
                    "• <b>المشرفين</b> ─ عرضهم\n"
                    "• <b>معلومات</b> ─ معلومات الجروب\n"
                    "• <b>حسابي</b> ─ إحصائياتك\n"
                    "• <b>رصيدي</b> ─ رصيدك\n"
                    "• <b>يومية</b> ─ راتبك اليومي\n"
                    "• <b>توب</b> ─ ترتيب النشطاء\n\n"
                    "🔒 <b>الإعدادات:</b>\n"
                    "• قفل_الروابط / فتح_الروابط\n"
                    "• قفل_التكرار / فتح_التكرار\n"
                    "• وغيرها...\n\n"
                    "⚙️ أرسل <b>الاعدادات</b> في الخاص\n"
                    "━━━━━━━━━━━━━━━━━━"
                )
                return
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            print("================ ERROR IN AUTO REPLY ================")
            print(err)
            print("=====================================================")
            try:
                await msg.answer(f"❌ <b>Error in auto_reply:</b>\n<pre>{err[-3000:]}</pre>")
            except:
                pass

    return router
