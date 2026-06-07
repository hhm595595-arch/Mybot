from datetime import datetime, date
import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from utils.helpers import is_admin


def bank_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💰 رصيدي", callback_data="eco_balance")],
        [InlineKeyboardButton(text="🎁 الراتب اليومي", callback_data="eco_daily")],
        [InlineKeyboardButton(text="📊 ترتيب الأغنياء", callback_data="eco_rich")],
        [InlineKeyboardButton(text="🎮 الألعاب", callback_data="eco_games")],
        [InlineKeyboardButton(text="🔙 العودة", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def PrivateEconomyRouter() -> Router:
    router = Router(name="private_economy")

    @router.callback_query(F.data == "eco_balance")
    async def show_balance(cq: CallbackQuery):
        await cq.answer()
        user = cq.from_user
        # Show balance for all groups the user is in (in private, we need chat context)
        # For simplicity, show a generic balance message
        await cq.message.edit_text(
            f"💰 <b>نظام البنك الافتراضي</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 {user.full_name}\n\n"
            f"⚠️ لعرض رصيدك في مجموعة معينة،\n"
            f"أرسل <b>رصيدي</b> في المجموعة\n\n"
            f"💡 استخدم الأزرار أدناه:",
            reply_markup=bank_keyboard()
        )

    @router.callback_query(F.data == "eco_daily")
    async def daily_reward(cq: CallbackQuery):
        await cq.answer()
        user = cq.from_user
        today = date.today().isoformat()

        # Check if already claimed today
        last = await db.get_last_daily(user.id, 0)  # global daily claim
        if last == today:
            await cq.message.edit_text(
                "❌ <b>لقد استلمت راتبك اليومي مسبقاً!</b>\n"
                "ارجع غداً للحصول على راتب جديد 🎁\n"
                "━━━━━━━━━━━━━━",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_bank")]
                ])
            )
            return

        amount = random.randint(50, 150)
        await db.set_last_daily(user.id, 0, today)
        # Use a global balance stored in a special "group"
        current = await db.get_balance(0, user.id)
        await db.set_balance(0, user.id, current + amount)

        await cq.message.edit_text(
            f"🎁 <b>الراتب اليومي!</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 {user.full_name}\n"
            f"💰 حصلت على: <b>+{amount}</b> نقطة\n"
            f"💵 رصيدك الكلي: <b>{current + amount:,}</b> نقطة\n"
            f"━━━━━━━━━━━━━━\n"
            f"📌 تعال بكرة عشان راتب جديد!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_bank")]
            ])
        )

    @router.callback_query(F.data == "eco_rich")
    async def show_richest(cq: CallbackQuery):
        await cq.answer()
        users = await db.get_richest(0, 10)
        lines = ["🏆 <b>ترتيب الأغنياء</b>\n━━━━━━━━━━━━━━"]
        if not users:
            lines.append("لا يوجد أغنياء بعد!")
        else:
            for i, u in enumerate(users, 1):
                try:
                    member = await cq.bot.get_chat(u["user_id"])
                    name = member.full_name
                except Exception:
                    name = f"ID: {u['user_id']}"
                lines.append(f"{i}. {name} ─ <b>{u['balance']:,}</b> نقطة")
        lines.append("━━━━━━━━━━━━━━")

        await cq.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_bank")]
            ])
        )

    @router.callback_query(F.data == "eco_games")
    async def games_menu(cq: CallbackQuery):
        await cq.answer()
        await cq.message.edit_text(
            "🎮 <b>🎪 صالة الألعاب</b>\n"
            "━━━━━━━━━━━━━━\n"
            "🎯 اختر لعبتك المفضلة:\n"
            "━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🪨📄✂️ حجر ورقة مقص", callback_data="game_rps")],
                [InlineKeyboardButton(text="🔮 حظك اليوم", callback_data="game_fortune")],
                [InlineKeyboardButton(text="🧩 فزورة", callback_data="game_riddle")],
                [InlineKeyboardButton(text="🎲 مراهنة", callback_data="game_bet")],
                [InlineKeyboardButton(text="🪙 قلب عملة", callback_data="game_coin")],
                [InlineKeyboardButton(text="🎲 زهر الحظ", callback_data="game_dice")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="section_bank")],
            ])
        )

    return router
