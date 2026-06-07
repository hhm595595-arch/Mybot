import random
import uuid

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import db

RPS_OPTIONS = {"🪨": "حجر", "📄": "ورقة", "✂️": "مقص"}
RPS_CHOICES = ["حجر", "ورقة", "مقص"]
RPS_WINS = {"حجر": "مقص", "ورقة": "حجر", "مقص": "ورقة"}
RPS_EMOJI = {"حجر": "🪨", "ورقة": "📄", "مقص": "✂️"}

RIDDLES = [
    ("شيء له أوراق ولكنه ليس نباتاً؟", "الكتاب"),
    ("شيء كلما أخذت منه يكبر؟", "الحفرة"),
    ("شيء يكسو الناس وهو عارٍ؟", "الإبرة"),
    ("شيء لا يبتل حتى في الماء؟", "الظل"),
    ("شيء له رقبة وليس له رأس؟", "الزجاجة"),
    ("شيء يمر من الزجاج ولا يكسره؟", "الضوء"),
    ("شيء يسمع ولا يتكلم؟", "الهاتف"),
    ("شيء يمشي بلا أرجل؟", "السحاب"),
    ("شيء له عين ولا يرى؟", "الإبرة"),
    ("شيء تأكله قبل أن يولد؟", "البصل"),
    ("شيء إذا دخل الماء لم يبتل؟", "الضوء"),
    ("شيء لا يتكلم وإذا أكل صدق؟", "الصدى"),
    ("شيء كلما زاد نقص؟", "العمر"),
    ("شيء إذا غاب عنك تتمنى رؤيته وإذا رأيته تخاف منه؟", "القمر"),
    ("شيء تطؤه وهو مبلول ولا يبتل؟", "الطريق"),
    ("شيء لا يمكن كسره؟", "البداية"),
    ("شيء يخترق الغابات والصحاري دون أن يتحرك؟", "الطريق"),
    ("شيء ينبض بلا قلب؟", "الساعة"),
]

FORTUNES = [
    "🌟 <b>حظك اليوم:</b> يوم رائع بانتظارك! استعد للمفاجآت الجميلة 🎉",
    "🌟 <b>حظك اليوم:</b> ستقابل شخصاً مهماً يغير حياتك! 🤝",
    "🌟 <b>حظك اليوم:</b> ريال مدريد يفوز وانت تكسب رهان! 😎⚽",
    "🌟 <b>حظك اليوم:</b> ابتعد عن القرارات المصيرية اليوم 👀",
    "🌟 <b>حظك اليوم:</b> خبر حلو يوصلك من شخص غائب 📩",
    "🌟 <b>حظك اليوم:</b> يوم مليء بالإنجازات! انطلق 💪🚀",
    "🌟 <b>حظك اليوم:</b> رزق واسع ينتظرك! ابشر 💰✨",
    "🌟 <b>حظك اليوم:</b> بداية جديدة لمشروع ناجح 📈🎯",
    "🌟 <b>حظك اليوم:</b> سفر أو تغيير مكان قريب 🧳✈️",
    "🌟 <b>حظك اليوم:</b> نجاح باهر في العمل أو الدراسة 🏆🎓",
    "🌟 <b>حظك اليوم:</b> يوم عاطفي جميل ينتظرك 💕",
    "🌟 <b>حظك اليوم:</b> صحة وعافية لك ولأهلك 🤍",
    "🌟 <b>حظك اليوم:</b> حل لمشكلة كانت تقلقك! 🧩✅",
    "🌟 <b>حظك اليوم:</b> صديق قديم يتذكرك ويبحث عنك 📞",
    "🌟 <b>حظك اليوم:</b> يوم حظك يبتسم لك، اغتنم الفرصة! 🍀",
]


def PrivateGamesRouter() -> Router:
    router = Router(name="private_games")

    # ── RPS ──
    @router.callback_query(F.data == "game_rps")
    async def rps_menu(cq: CallbackQuery):
        await cq.answer()
        bot_user = await cq.bot.me()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 اللعب مع البوت", callback_data="rps_play_bot")],
            [InlineKeyboardButton(text="👥 اللعب مع صديق آخر", switch_inline_query="rps")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
        ])
        await cq.message.edit_text(
            "🎮 <b>🪨📄✂️ حجر ورقة مقص</b>\n"
            "━━━━━━━━━━━━━━\n"
            "اختر طريقة اللعب التي تفضلها:\n"
            "🤖 <b>مع البوت:</b> ستلعب ضدي مباشرة.\n"
            "👥 <b>مع صديق:</b> ستقوم باختيار محادثة صديقك وتلعب معه عبر الإنلاين.",
            reply_markup=keyboard
        )

    @router.callback_query(F.data == "rps_play_bot")
    async def rps_bot_menu(cq: CallbackQuery):
        await cq.answer()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🪨 حجر", callback_data="rps_choice:حجر"),
             InlineKeyboardButton(text="📄 ورقة", callback_data="rps_choice:ورقة"),
             InlineKeyboardButton(text="✂️ مقص", callback_data="rps_choice:مقص")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="game_rps")],
        ])
        await cq.message.edit_text(
            "🎮 <b>🪨📄✂️ حجر ورقة مقص (ضد البوت)</b>\n"
            "━━━━━━━━━━━━━━\n"
            "اختر سلاحك:",
            reply_markup=keyboard
        )

    @router.callback_query(F.data.startswith("rps_choice:"))
    async def rps_play(cq: CallbackQuery):
        await cq.answer()
        user_choice = cq.data.split(":")[1]
        bot_choice = random.choice(RPS_CHOICES)

        if user_choice == bot_choice:
            result = "🤝 <b>تعادل!</b>"
        elif RPS_WINS[user_choice] == bot_choice:
            result = "🎉 <b>فزت!</b> 🎉\n💰 ربحت 10 نقاط"
            await db.add_balance(0, cq.from_user.id, 10)
        else:
            result = "😅 <b>خسرت!</b>"

        await cq.message.edit_text(
            f"🎮 <b>🪨📄✂️ حجر ورقة مقص</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 أنت: {RPS_EMOJI[user_choice]} {user_choice}\n"
            f"🤖 ريو: {RPS_EMOJI[bot_choice]} {bot_choice}\n"
            f"━━━━━━━━━━━━━━\n"
            f"{result}\n"
            f"━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 العب مرة أخرى", callback_data="rps_play_bot")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="game_rps")],
            ])
        )

    # ── Fortune ──
    @router.callback_query(F.data == "game_fortune")
    async def fortune_tell(cq: CallbackQuery):
        await cq.answer()
        fortune = random.choice(FORTUNES)
        await cq.message.edit_text(
            f"🔮 <b>حظك اليوم يا {cq.from_user.full_name}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{fortune}\n"
            f"━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 مرة أخرى", callback_data="game_fortune")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
            ])
        )

    # ── Riddle ──
    @router.callback_query(F.data == "game_riddle")
    async def riddle_start(cq: CallbackQuery):
        await cq.answer()
        riddle, answer = random.choice(RIDDLES)
        riddle_id = uuid.uuid4().hex[:8]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👀 شوف الحل", callback_data=f"riddle_ans:{riddle_id}:{answer}")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
        ])
        await cq.message.edit_text(
            f"🧩 <b>فزورة</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{riddle}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🤔 فكر قبل ما تشوف الحل!",
            reply_markup=keyboard
        )

    @router.callback_query(F.data.startswith("riddle_ans:"))
    async def riddle_answer(cq: CallbackQuery):
        await cq.answer()
        parts = cq.data.split(":", 2)
        if len(parts) < 3:
            return
        answer = parts[2]
        await cq.message.edit_text(
            f"🧩 <b>حل الفزورة</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"💡 الإجابة: <b>{answer}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎉 هل حليتها صح؟ 😎",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 فزورة أخرى", callback_data="game_riddle")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
            ])
        )

    # ── Bet ──
    @router.callback_query(F.data == "game_bet")
    async def bet_menu(cq: CallbackQuery):
        await cq.answer()
        user_id = cq.from_user.id
        balance = await db.get_balance(0, user_id)
        await cq.message.edit_text(
            f"🎲 <b>🎰 المراهنة</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 رصيدك: <b>{balance:,}</b> نقطة\n\n"
            f"📌 اختر مبلغ المراهنة:\n"
            f"(ربح 1.8× 💲)",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="10 🪙", callback_data="bet_do:10"),
                 InlineKeyboardButton(text="25 🪙", callback_data="bet_do:25"),
                 InlineKeyboardButton(text="50 🪙", callback_data="bet_do:50")],
                [InlineKeyboardButton(text="100 🪙", callback_data="bet_do:100"),
                 InlineKeyboardButton(text="250 🪙", callback_data="bet_do:250"),
                 InlineKeyboardButton(text="500 🪙", callback_data="bet_do:500")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
            ])
        )

    @router.callback_query(F.data.startswith("bet_do:"))
    async def bet_play(cq: CallbackQuery):
        await cq.answer()
        amount = int(cq.data.split(":")[1])
        user_id = cq.from_user.id
        balance = await db.get_balance(0, user_id)

        if balance < amount:
            await cq.message.edit_text(
                "❌ <b>رصيدك غير كافٍ!</b>\n"
                "اجمع نقاط أكثر من الراتب اليومي 🎁",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="game_bet")]
                ])
            )
            return

        won = random.random() < 0.45
        if won:
            win_amount = int(amount * 1.8)
            new_bal = await db.add_balance(0, user_id, win_amount)
            await cq.message.edit_text(
                f"🎲 <b>🎰 المراهنة!</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎉🎉 <b>فزت!</b> 🎉🎉\n"
                f"💰 ربحت: <b>+{win_amount:,}</b> نقطة\n"
                f"💵 رصيدك: <b>{new_bal:,}</b> نقطة\n"
                f"━━━━━━━━━━━━━━",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 العب مرة أخرى", callback_data="game_bet")],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
                ])
            )
        else:
            await db.add_balance(0, user_id, -amount)
            new_bal = await db.get_balance(0, user_id)
            await cq.message.edit_text(
                f"🎲 <b>🎰 المراهنة!</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"😅 <b>خسرت!</b> 😅\n"
                f"💰 خسرت: <b>-{amount:,}</b> نقطة\n"
                f"💵 رصيدك: <b>{new_bal:,}</b> نقطة\n"
                f"━━━━━━━━━━━━━━",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 جرب حظك مرة أخرى", callback_data="game_bet")],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
                ])
            )

    # ── Coin Flip ──
    @router.callback_query(F.data == "game_coin")
    async def coin_flip(cq: CallbackQuery):
        await cq.answer()
        result = random.choice(["وجه 🟡", "كتابة 🔴"])
        outcome = "🎉 <b>فزت!</b> 🎉" if "وجه" in result else "😅 <b>خسرت!</b>"
        await cq.message.edit_text(
            f"🪙 <b>قلب العملة</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🪙 <b>{result}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{outcome}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 مرة أخرى", callback_data="game_coin")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
            ])
        )

    # ── Dice ──
    @router.callback_query(F.data == "game_dice")
    async def dice_roll(cq: CallbackQuery):
        await cq.answer()
        dice = random.randint(1, 6)
        dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        emoji = dice_emoji[dice]
        await cq.message.edit_text(
            f"🎲 <b>زهر الحظ</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{emoji} <b>{dice}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{'🎉 رقم كبير!' if dice >= 5 else '😅 رقم صغير!'}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎲 دحرج مرة أخرى", callback_data="game_dice")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="eco_games")],
            ])
        )

    return router
