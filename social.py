from aiogram import Router, F
from aiogram.types import Message
from database import db
from utils.helpers import format_date

def GroupSocialRouter() -> Router:
    router = Router(name="group_social")

    # ── Marriages ──
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("ارتباط"))
    async def marry_cmd(msg: Message):
        if not msg.reply_to_message:
            await msg.reply("❌ بالرد على العضو: ارتباط")
            return
        
        target = msg.reply_to_message.from_user
        if target.id == msg.from_user.id or target.is_bot:
            return
            
        m1 = await db.get_marriage(msg.from_user.id)
        m2 = await db.get_marriage(target.id)
        
        if m1 or m2:
            await msg.reply("❌ أحدكما مرتبط بالفعل!")
            return
            
        await db.marry(msg.from_user.id, target.id, format_date())
        await msg.reply(f"💍 <b>ألف مبروك!</b>\n🎉 تم ارتباط {msg.from_user.full_name} و {target.full_name}")

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["عائلتي", "زواجي", "ارتباطي"]))
    async def my_family_cmd(msg: Message):
        m = await db.get_marriage(msg.from_user.id)
        if not m:
            await msg.reply("❌ أنت غير مرتبط حالياً. (استخدم: ارتباط بالرد على شخص)")
            return
            
        partner_id = m["user1_id"] if m["user2_id"] == msg.from_user.id else m["user2_id"]
        partner_name = f"ID: {partner_id}"
        try:
            chat_member = await msg.chat.get_member(partner_id)
            partner_name = chat_member.user.full_name
        except:
            pass
            
        await msg.reply(
            f"❤️ <b>معلومات الارتباط</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👫 الشريك: <b>{partner_name}</b>\n"
            f"🗓️ تاريخ الارتباط: {m['marriage_date']}\n"
            f"💰 الرصيد المشترك: {m['joint_balance']:,} نقطة"
        )
        
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["طلاق", "انفصال"]))
    async def divorce_cmd(msg: Message):
        m = await db.get_marriage(msg.from_user.id)
        if not m:
            return
        await db.divorce(msg.from_user.id)
        await msg.reply("💔 <b>تم الانفصال بنجاح.</b>")
        
    # ── Clans ──
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.startswith("تأسيس "))
    async def create_clan_cmd(msg: Message):
        clan_name = msg.text.split(maxsplit=1)[1]
        bal = await db.get_balance(msg.chat.id, msg.from_user.id)
        if bal < 10000:
            await msg.reply("❌ تأسيس العشيرة يتطلب <b>10,000</b> نقطة!")
            return
            
        existing = await db.get_clan_by_name(clan_name)
        if existing:
            await msg.reply("❌ هذا الاسم محجوز لعشيرة أخرى.")
            return
            
        in_clan = await db.get_user_clan(msg.from_user.id)
        if in_clan:
            await msg.reply("❌ أنت بالفعل عضو في عشيرة.")
            return
            
        await db.add_balance(msg.chat.id, msg.from_user.id, -10000)
        await db.create_clan(clan_name, msg.from_user.id, format_date())
        await msg.reply(f"🏰 <b>تم تأسيس عشيرة '{clan_name}' بنجاح!</b>")
        
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["عشيرتي"]))
    async def my_clan_cmd(msg: Message):
        c = await db.get_user_clan(msg.from_user.id)
        if not c:
            await msg.reply("❌ أنت لست في أي عشيرة.")
            return
            
        await msg.reply(
            f"🏰 <b>عشيرة {c['name']}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🌟 مستوى الخبرة (XP): {c['xp']}\n"
            f"💰 بنك العشيرة: {c['balance']:,} نقطة\n"
            f"🗓️ تاريخ التأسيس: {c['created_at']}"
        )
        
    # ── Leveling ──
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["مستواي", "لفلي", "مستوى"]))
    async def my_level_cmd(msg: Message):
        row = await db._fetchone("SELECT level, xp FROM members WHERE chat_id=? AND user_id=?", [msg.chat.id, msg.from_user.id])
        if not row:
            return
            
        req_xp = row["level"] * 50
        await msg.reply(
            f"🌟 <b>مستواك الحالي</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 {msg.from_user.full_name}\n"
            f"🎖️ المستوى: <b>{row['level']}</b>\n"
            f"✨ الخبرة (XP): <b>{row['xp']}/{req_xp}</b>"
        )
        
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["توب_المستويات", "المستويات"]))
    async def top_levels_cmd(msg: Message):
        users = await db.get_top_levels(msg.chat.id, 10)
        lines = ["🏆 <b>أعلى المستويات في الجروب</b>\n━━━━━━━━━━━━━━"]
        for i, u in enumerate(users, 1):
            try:
                member = await msg.chat.get_member(u["user_id"])
                name = member.user.full_name
            except Exception:
                name = f"ID: {u['user_id']}"
            lines.append(f"{i}. {name} ─ لفل <b>{u['level']}</b> (XP: {u['xp']})")
        lines.append("━━━━━━━━━━━━━━")
        await msg.reply("\n".join(lines))

    # ── Fun & Social (ترفيه وتفاعل) ──
    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["زوجني", "زواج", "عريس", "عروسة"]))
    async def random_marry_cmd(msg: Message):
        import random
        users = await db.get_top_messages(msg.chat.id, 50)
        if len(users) < 2:
            await msg.reply("❌ مفيش ناس كفاية في الجروب عشان أزوجك 😂")
            return
            
        candidates = [u for u in users if u["user_id"] != msg.from_user.id]
        if not candidates:
            await msg.reply("❌ مفيش حد غيرك نشط في الجروب، روح اتزوج نفسك 😂")
            return
            
        target = random.choice(candidates)
        try:
            member = await msg.chat.get_member(target["user_id"])
            target_name = member.user.full_name
            target_id = member.user.id
        except:
            await msg.reply("❌ حدث خطأ، النصيب مجاش لسه 😂")
            return
            
        await msg.reply(
            f"🎉 <b>إعلان زواج عشوائي!</b> 💍\n"
            f"━━━━━━━━━━━━━━\n"
            f"🤵/👰 من: <b>{msg.from_user.full_name}</b>\n"
            f"💘 تم التوفيق مع: <a href='tg://user?id={target_id}'><b>{target_name}</b></a>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎊 بالرفاء والبنين! 😂🏃‍♂️"
        )

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["نسبة الحب", "نسبه الحب"]))
    async def love_percentage_cmd(msg: Message):
        import random
        if not msg.reply_to_message:
            await msg.reply("❌ بالرد على الشخص عشان أعرف أقيس الحب! 😂")
            return
            
        target = msg.reply_to_message.from_user
        if target.id == msg.from_user.id:
            await msg.reply("❌ بتحب نفسك؟ نسبة حبك لنفسك 1000% يا نرجسي 😂")
            return
            
        percentage = random.randint(0, 100)
        comment = ""
        if percentage < 20:
            comment = "💔 مفيش أي أمل، ابعد أحسن 😂"
        elif percentage < 50:
            comment = "🥀 محتاجين شغل كتير عشان تحبوا بعض."
        elif percentage < 80:
            comment = "💖 في إعجاب، استمروا!"
        else:
            comment = "🔥 حب أسطوري! متى الفرح؟ 😍"
            
        await msg.reply(
            f"❤️ <b>مقياس الحب</b> 🌡️\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 {msg.from_user.full_name}\n"
            f"💘 <b>{percentage}%</b> 💘\n"
            f"👤 {target.full_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💬 {comment}"
        )

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["حظي", "حظي اليوم"]))
    async def my_luck_cmd(msg: Message):
        import random
        percentage = random.randint(1, 100)
        messages = [
            "اليوم يومك، انطلق! 🚀",
            "خد بالك من قراراتك اليوم 🤔",
            "أخبار مفرحة في الطريق إليك 🎁",
            "خليك في البيت أحسن لك النهاردة 😂",
            "شخص غالي سيتصل بك قريباً 📱"
        ]
        await msg.reply(
            f"🍀 <b>حظك اليوم</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"📊 نسبة حظك: <b>{percentage}%</b>\n"
            f"💡 <i>{random.choice(messages)}</i>"
        )

    TRIVIA_QUESTIONS = [
        {"q": "ما هي عاصمة السعودية؟", "a": ["الرياض", "رياض"]},
        {"q": "كم عدد كواكب المجموعة الشمسية؟", "a": ["8", "ثمانية"]},
        {"q": "ما هو أكبر محيط في العالم؟", "a": ["الهادي", "المحيط الهادي"]},
        {"q": "ما هو أطول نهر في العالم؟", "a": ["النيل", "نهر النيل"]},
        {"q": "من هو مخترع المصباح الكهربائي؟", "a": ["أديسون", "توماس أديسون"]},
        {"q": "ما هو الغاز الذي نتنفسه ويعطينا الحياة؟", "a": ["الأكسجين", "الاكسجين", "اكسجين"]},
        {"q": "حيوان يُطلق عليه 'سفينة الصحراء'؟", "a": ["الجمل", "جمل"]},
        {"q": "ما هو أسرع حيوان بري؟", "a": ["الفهد", "فهد"]},
        {"q": "من هو خاتم الأنبياء؟", "a": ["محمد", "النبي محمد", "محمد صلى الله عليه وسلم"]}
    ]

    ACTIVE_QUESTIONS = {}

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["سؤال", "اسئلة", "لعبة"]))
    async def ask_question_cmd(msg: Message):
        import random
        chat_id = msg.chat.id
        if chat_id in ACTIVE_QUESTIONS:
            await msg.reply("❌ هناك سؤال مفعل حالياً، أجب عليه أولاً! (لإلغائه اكتب: الغاء_السؤال)")
            return
            
        q = random.choice(TRIVIA_QUESTIONS)
        ACTIVE_QUESTIONS[chat_id] = q
        
        await msg.answer(
            f"🎯 <b>لعبة الأسئلة!</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"❓ <b>السؤال:</b> {q['q']}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 <b>الجائزة:</b> 100 نقطة (لأول إجابة صحيحة)\n"
            f"✍️ أرسل إجابتك مباشرة في الجروب!"
        )

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["الغاء_السؤال", "تخطي_السؤال"]))
    async def cancel_question_cmd(msg: Message):
        from utils.helpers import is_admin
        chat_id = msg.chat.id
        if chat_id in ACTIVE_QUESTIONS:
            if await is_admin(msg.chat, msg.from_user.id):
                ACTIVE_QUESTIONS.pop(chat_id)
                await msg.reply("✅ تم إلغاء السؤال الحالي.")
            else:
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                
    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.text, 
        lambda msg: msg.chat.id in ACTIVE_QUESTIONS
    )
    async def answer_checker(msg: Message):
        chat_id = msg.chat.id
        q = ACTIVE_QUESTIONS[chat_id]
        answer = msg.text.strip().lower()
        
        if answer in q['a']:
            ACTIVE_QUESTIONS.pop(chat_id)
            await db.add_balance(chat_id, msg.from_user.id, 100)
            await msg.reply(
                f"🎉 <b>إجابة صحيحة!</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 الفائز: {msg.from_user.full_name}\n"
                f"🎁 الجائزة: 100 نقطة\n"
                f"━━━━━━━━━━━━━━\n"
                f"لطلب سؤال آخر اكتب: <b>سؤال</b>"
            )

    ACTIVE_ROULETTES = {}

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.func(lambda t: t and t.strip().lower().startswith("روليت")))
    async def start_roulette_cmd(msg: Message):
        from utils.helpers import is_admin
        chat_id = msg.chat.id
        
        # Check if user is starting or participating
        text = msg.text.strip().lower()
        if text == "روليت":
            prize = "جائزة مميزة"
        else:
            prize = text[5:].strip()
            
        if not await is_admin(msg.chat, msg.from_user.id):
            await msg.reply("❌ هذا الأمر للمشرفين فقط.")
            return
            
        if chat_id in ACTIVE_ROULETTES:
            await msg.reply("❌ هناك لعبة روليت شغالة بالفعل! (للسحب اكتب: سحب الروليت)")
            return
            
        ACTIVE_ROULETTES[chat_id] = {
            "prize": prize,
            "participants": {}
        }
        
        await msg.answer(
            f"🎰 <b>لعبة الروليت بدأت!</b> 🎉\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎁 <b>الجائزة:</b> {prize}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👇 <b>للمشاركة:</b> أرسل كلمة <code>دخول</code>\n"
            f"👑 <b>للمشرف:</b> أرسل <code>سحب</code> لإعلان الفائز!"
        )

    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.text.in_(["دخول", "انا", "مشاركة"]),
        lambda msg: msg.chat.id in ACTIVE_ROULETTES
    )
    async def join_roulette_cmd(msg: Message):
        chat_id = msg.chat.id
        roulette = ACTIVE_ROULETTES[chat_id]
        user_id = msg.from_user.id
        
        if user_id in roulette["participants"]:
            await msg.reply("❌ أنت مشارك بالفعل!")
            return
            
        roulette["participants"][user_id] = msg.from_user.full_name
        count = len(roulette["participants"])
        await msg.reply(f"✅ تم تسجيلك! (عدد المشاركين الآن: {count})")

    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.text.in_(["سحب", "سحب الروليت", "فر", "فر الروليت", "فرها"]),
        lambda msg: msg.chat.id in ACTIVE_ROULETTES
    )
    async def draw_roulette_cmd(msg: Message):
        from utils.helpers import is_admin
        import random
        chat_id = msg.chat.id
        
        if not await is_admin(msg.chat, msg.from_user.id):
            await msg.reply("❌ المشرف فقط يمكنه السحب!")
            return
            
        roulette = ACTIVE_ROULETTES[chat_id]
        participants = roulette["participants"]
        
        if not participants:
            await msg.reply("❌ لم يشارك أحد في الروليت! تم إلغاء اللعبة.")
            ACTIVE_ROULETTES.pop(chat_id)
            return
            
        winner_id = random.choice(list(participants.keys()))
        winner_name = participants[winner_id]
        prize = roulette["prize"]
        
        ACTIVE_ROULETTES.pop(chat_id)
        
        await msg.answer(
            f"🎰 <b>نتيجة الروليت!</b> 🎰\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎁 <b>الجائزة:</b> {prize}\n"
            f"👥 <b>عدد المشاركين:</b> {len(participants)}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎉 <b>الفائز هو:</b> <a href='tg://user?id={winner_id}'><b>{winner_name}</b></a> 🎊\n"
            f"✨ ألف مبرووووك! تواصل مع المشرف لاستلام جائزتك."
        )

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text.in_(["الغاء الروليت", "الغاء_الروليت"]))
    async def cancel_roulette_cmd(msg: Message):
        from utils.helpers import is_admin
        chat_id = msg.chat.id
        if chat_id in ACTIVE_ROULETTES:
            if await is_admin(msg.chat, msg.from_user.id):
                ACTIVE_ROULETTES.pop(chat_id)
                await msg.reply("✅ تم إلغاء الروليت بنجاح.")
            else:
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")

    return router
