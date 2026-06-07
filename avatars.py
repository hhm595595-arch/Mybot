from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


def avatars_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🖼️ افتارات بنات", callback_data="av_girl")],
        [InlineKeyboardButton(text="🖼️ افتارات شباب", callback_data="av_boy")],
        [InlineKeyboardButton(text="🖼️ افتارات كرتون", callback_data="av_cartoon")],
        [InlineKeyboardButton(text="🖼️ جداريات", callback_data="av_wall")],
        [InlineKeyboardButton(text="🔙 العودة", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


AVATAR_LINKS = {
    "av_girl": [
        "https://picsum.photos/seed/girl1/400/400",
        "https://picsum.photos/seed/girl2/400/400",
        "https://picsum.photos/seed/girl3/400/400",
        "https://picsum.photos/seed/girl4/400/400",
        "https://picsum.photos/seed/girl5/400/400",
    ],
    "av_boy": [
        "https://picsum.photos/seed/boy1/400/400",
        "https://picsum.photos/seed/boy2/400/400",
        "https://picsum.photos/seed/boy3/400/400",
        "https://picsum.photos/seed/boy4/400/400",
        "https://picsum.photos/seed/boy5/400/400",
    ],
    "av_cartoon": [
        "https://picsum.photos/seed/cartoon1/400/400",
        "https://picsum.photos/seed/cartoon2/400/400",
        "https://picsum.photos/seed/cartoon3/400/400",
        "https://picsum.photos/seed/cartoon4/400/400",
        "https://picsum.photos/seed/cartoon5/400/400",
    ],
    "av_wall": [
        "https://picsum.photos/seed/wall1/1920/1080",
        "https://picsum.photos/seed/wall2/1920/1080",
        "https://picsum.photos/seed/wall3/1920/1080",
        "https://picsum.photos/seed/wall4/1920/1080",
        "https://picsum.photos/seed/wall5/1920/1080",
    ],
}


CATEGORY_NAMES = {
    "av_girl": "🖼️ افتارات بنات",
    "av_boy": "🖼️ افتارات شباب",
    "av_cartoon": "🖼️ افتارات كرتون",
    "av_wall": "🖼️ جداريات",
}


def PrivateAvatarsRouter() -> Router:
    router = Router(name="private_avatars")

    @router.callback_query(F.data.in_(AVATAR_LINKS.keys()))
    async def show_avatar_category(cq: CallbackQuery):
        await cq.answer()
        category = cq.data
        links = AVATAR_LINKS[category]
        name = CATEGORY_NAMES.get(category, "🖼️ افتارات")

        keyboard = []
        for i, link in enumerate(links, 1):
            keyboard.append([
                InlineKeyboardButton(text=f"{i}", callback_data=f"av_show:{category}:{i-1}")
            ])
        keyboard.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="section_avatars")])

        await cq.message.edit_text(
            f"{name}\n━━━━━━━━━━━━━━\nاختر صورة لعرضها:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    @router.callback_query(F.data.startswith("av_show:"))
    async def show_avatar(cq: CallbackQuery):
        await cq.answer()
        parts = cq.data.split(":")
        if len(parts) < 3:
            return
        category = parts[1]
        idx = int(parts[2])
        links = AVATAR_LINKS.get(category, [])
        if idx >= len(links):
            return

        url = links[idx]
        await cq.message.answer_photo(
            photo=url,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data=category)],
            ])
        )

    return router
