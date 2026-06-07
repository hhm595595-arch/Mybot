import aiosqlite
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rio_data.db")


def _dict_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


class Database:
    def __init__(self):
        self._conn = None

    async def connect(self):
        self._conn = await aiosqlite.connect(DB_PATH)
        self._conn.row_factory = _dict_factory
        await self._create_tables()

    async def close(self):
        if self._conn:
            await self._conn.close()

    async def _create_tables(self):
        await self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT DEFAULT '',
                link_protection INTEGER DEFAULT 1,
                anti_flood INTEGER DEFAULT 1,
                bad_words_filter INTEGER DEFAULT 1,
                forward_protection INTEGER DEFAULT 0,
                welcome INTEGER DEFAULT 1,
                captcha INTEGER DEFAULT 1,
                auto_reply INTEGER DEFAULT 1,
                warn_limit INTEGER DEFAULT 3,
                rules TEXT DEFAULT '',
                custom_welcome TEXT DEFAULT '',
                is_active INTEGER DEFAULT 0,
                activated_by INTEGER DEFAULT 0,
                activated_at TEXT DEFAULT '',
                owner_id INTEGER DEFAULT 0,
                night_mode INTEGER DEFAULT 0,
                night_start INTEGER DEFAULT 22,
                night_end INTEGER DEFAULT 7,
                media_protection INTEGER DEFAULT 1,
                bot_protection INTEGER DEFAULT 1,
                long_msg_protection INTEGER DEFAULT 1,
                ranks_enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS members (
                chat_id INTEGER,
                user_id INTEGER,
                warns INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                messages INTEGER DEFAULT 0,
                join_date TEXT DEFAULT '',
                captcha_passed INTEGER DEFAULT 0,
                is_muted INTEGER DEFAULT 0,
                custom_rank TEXT DEFAULT '',
                is_admin INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS marriages (
                user1_id INTEGER,
                user2_id INTEGER,
                marriage_date TEXT,
                joint_balance INTEGER DEFAULT 0,
                PRIMARY KEY (user1_id)
            );
            CREATE TABLE IF NOT EXISTS clans (
                clan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                owner_id INTEGER,
                balance INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER,
                user_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS auto_replies (
                chat_id INTEGER,
                keyword TEXT,
                reply_text TEXT,
                PRIMARY KEY (chat_id, keyword)
            );
            CREATE TABLE IF NOT EXISTS bad_words (
                chat_id INTEGER,
                word TEXT,
                PRIMARY KEY (chat_id, word)
            );
            CREATE TABLE IF NOT EXISTS polls (
                chat_id INTEGER,
                poll_id TEXT,
                question TEXT,
                options TEXT,
                votes TEXT,
                is_open INTEGER DEFAULT 1,
                PRIMARY KEY (chat_id, poll_id)
            );
            CREATE TABLE IF NOT EXISTS bot_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                join_date TEXT
            );
            CREATE TABLE IF NOT EXISTS captcha (
                chat_id INTEGER,
                user_id INTEGER,
                answer TEXT,
                created_at REAL,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS daily_claims (
                user_id INTEGER,
                chat_id INTEGER,
                last_claim TEXT,
                PRIMARY KEY (user_id, chat_id)
            );
        """)
        await self._conn.commit()
        await self._migrate()

    async def _migrate(self):
        """Add new columns to existing tables safely"""
        migrations = [
            "ALTER TABLE groups ADD COLUMN is_active INTEGER DEFAULT 0",
            "ALTER TABLE groups ADD COLUMN activated_by INTEGER DEFAULT 0",
            "ALTER TABLE groups ADD COLUMN activated_at TEXT DEFAULT ''",
            "ALTER TABLE groups ADD COLUMN owner_id INTEGER DEFAULT 0",
            "ALTER TABLE groups ADD COLUMN night_mode INTEGER DEFAULT 0",
            "ALTER TABLE groups ADD COLUMN night_start INTEGER DEFAULT 22",
            "ALTER TABLE groups ADD COLUMN night_end INTEGER DEFAULT 7",
            "ALTER TABLE groups ADD COLUMN auto_reply INTEGER DEFAULT 1",
            "ALTER TABLE members ADD COLUMN is_admin INTEGER DEFAULT 0",
            "ALTER TABLE groups ADD COLUMN media_protection INTEGER DEFAULT 1",
            "ALTER TABLE groups ADD COLUMN bot_protection INTEGER DEFAULT 1",
            "ALTER TABLE groups ADD COLUMN long_msg_protection INTEGER DEFAULT 1",
            "ALTER TABLE members ADD COLUMN xp INTEGER DEFAULT 0",
            "ALTER TABLE members ADD COLUMN level INTEGER DEFAULT 1",
            "ALTER TABLE groups ADD COLUMN ranks_enabled INTEGER DEFAULT 1",
        ]
        for sql in migrations:
            try:
                await self._conn.execute(sql)
            except Exception:
                pass
        await self._conn.commit()

    async def _execute(self, sql, params=None):
        cur = await self._conn.execute(sql, params or [])
        await self._conn.commit()
        return cur

    async def _fetchone(self, sql, params=None):
        cur = await self._conn.execute(sql, params or [])
        return await cur.fetchone()

    async def _fetchall(self, sql, params=None):
        cur = await self._conn.execute(sql, params or [])
        return await cur.fetchall()

    # ── Group settings ──

    async def ensure_group(self, chat_id: int, title: str = ""):
        existing = await self._fetchone("SELECT chat_id FROM groups WHERE chat_id=?", [chat_id])
        if not existing:
            await self._execute("INSERT INTO groups (chat_id, title) VALUES (?, ?)", [chat_id, title])

    async def get_setting(self, chat_id: int, key: str):
        row = await self._fetchone(f"SELECT {key} FROM groups WHERE chat_id=?", [chat_id])
        return row[key] if row else None

    async def set_setting(self, chat_id: int, key: str, value):
        await self.ensure_group(chat_id)
        await self._execute(f"UPDATE groups SET {key}=? WHERE chat_id=?", [value, chat_id])

    async def get_rules(self, chat_id: int) -> str:
        row = await self._fetchone("SELECT rules FROM groups WHERE chat_id=?", [chat_id])
        return row["rules"] if row else ""

    async def set_rules(self, chat_id: int, rules: str):
        await self.ensure_group(chat_id)
        await self._execute("UPDATE groups SET rules=? WHERE chat_id=?", [rules, chat_id])

    async def get_warn_limit(self, chat_id: int) -> int:
        row = await self._fetchone("SELECT warn_limit FROM groups WHERE chat_id=?", [chat_id])
        return row["warn_limit"] if row else 3

    async def set_warn_limit(self, chat_id: int, limit: int):
        await self.ensure_group(chat_id)
        await self._execute("UPDATE groups SET warn_limit=? WHERE chat_id=?", [limit, chat_id])

    # ── Members ──

    async def ensure_member(self, chat_id: int, user_id: int):
        existing = await self._fetchone(
            "SELECT user_id FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        if not existing:
            await self._execute(
                "INSERT INTO members (chat_id, user_id) VALUES (?, ?)", [chat_id, user_id]
            )

    async def get_warns(self, chat_id: int, user_id: int) -> int:
        await self.ensure_member(chat_id, user_id)
        row = await self._fetchone(
            "SELECT warns FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["warns"] if row else 0

    async def add_warn(self, chat_id: int, user_id: int, reason: str = "") -> int:
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET warns=warns+1 WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        row = await self._fetchone(
            "SELECT warns FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["warns"]

    async def remove_warn(self, chat_id: int, user_id: int) -> int:
        await self.ensure_member(chat_id, user_id)
        cur = await self._execute(
            "UPDATE members SET warns=MAX(0,warns-1) WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        row = await self._fetchone(
            "SELECT warns FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["warns"] if row else 0

    async def reset_warns(self, chat_id: int, user_id: int):
        await self._execute(
            "UPDATE members SET warns=0 WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )

    async def get_messages_count(self, chat_id: int, user_id: int) -> int:
        await self.ensure_member(chat_id, user_id)
        row = await self._fetchone(
            "SELECT messages FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["messages"] if row else 0

    async def add_message(self, chat_id: int, user_id: int):
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET messages=messages+1 WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )

    async def get_balance(self, chat_id: int, user_id: int) -> int:
        await self.ensure_member(chat_id, user_id)
        row = await self._fetchone(
            "SELECT balance FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["balance"] if row else 0

    async def set_balance(self, chat_id: int, user_id: int, amount: int):
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET balance=? WHERE chat_id=? AND user_id=?", [amount, chat_id, user_id]
        )

    async def add_balance(self, chat_id: int, user_id: int, amount: int) -> int:
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET balance=balance+? WHERE chat_id=? AND user_id=?", [amount, chat_id, user_id]
        )
        row = await self._fetchone(
            "SELECT balance FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["balance"]

    async def get_richest(self, chat_id: int, limit: int = 10):
        rows = await self._fetchall(
            "SELECT user_id, balance FROM members WHERE chat_id=? ORDER BY balance DESC LIMIT ?",
            [chat_id, limit]
        )
        return rows

    async def set_join_date(self, chat_id: int, user_id: int, date_str: str):
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET join_date=? WHERE chat_id=? AND user_id=?", [date_str, chat_id, user_id]
        )

    async def get_join_date(self, chat_id: int, user_id: int) -> str:
        row = await self._fetchone(
            "SELECT join_date FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["join_date"] if row else ""

    async def set_captcha_passed(self, chat_id: int, user_id: int, passed: int = 1):
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET captcha_passed=? WHERE chat_id=? AND user_id=?", [passed, chat_id, user_id]
        )

    async def has_passed_captcha(self, chat_id: int, user_id: int) -> bool:
        row = await self._fetchone(
            "SELECT captcha_passed FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return bool(row["captcha_passed"]) if row else False

    async def set_custom_rank(self, chat_id: int, user_id: int, rank: str):
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET custom_rank=? WHERE chat_id=? AND user_id=?", [rank, chat_id, user_id]
        )

    async def get_custom_rank(self, chat_id: int, user_id: int) -> str:
        row = await self._fetchone(
            "SELECT custom_rank FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )
        return row["custom_rank"] if row else ""

    async def get_top_messages(self, chat_id: int, limit: int = 10):
        rows = await self._fetchall(
            "SELECT user_id, messages FROM members WHERE chat_id=? ORDER BY messages DESC LIMIT ?",
            [chat_id, limit]
        )
        return rows

    async def get_top_warns(self, chat_id: int, limit: int = 10):
        rows = await self._fetchall(
            "SELECT user_id, warns FROM members WHERE chat_id=? ORDER BY warns DESC LIMIT ?",
            [chat_id, limit]
        )
        return rows

    # ── Auto replies ──

    async def get_custom_replies(self, chat_id: int) -> dict:
        rows = await self._fetchall(
            "SELECT keyword, reply_text FROM auto_replies WHERE chat_id=?", [chat_id]
        )
        return {r["keyword"]: r["reply_text"] for r in rows}

    async def add_custom_reply(self, chat_id: int, keyword: str, reply_text: str):
        await self._execute(
            "INSERT OR REPLACE INTO auto_replies (chat_id, keyword, reply_text) VALUES (?, ?, ?)",
            [chat_id, keyword, reply_text]
        )

    async def remove_custom_reply(self, chat_id: int, keyword: str):
        await self._execute(
            "DELETE FROM auto_replies WHERE chat_id=? AND keyword=?", [chat_id, keyword]
        )

    # ── Bad words ──

    async def get_bad_words(self, chat_id: int) -> list:
        rows = await self._fetchall(
            "SELECT word FROM bad_words WHERE chat_id=?", [chat_id]
        )
        return [r["word"] for r in rows]

    async def add_bad_word(self, chat_id: int, word: str):
        await self._execute(
            "INSERT OR IGNORE INTO bad_words (chat_id, word) VALUES (?, ?)", [chat_id, word]
        )

    async def remove_bad_word(self, chat_id: int, word: str):
        await self._execute(
            "DELETE FROM bad_words WHERE chat_id=? AND word=?", [chat_id, word]
        )

    # ── Captcha ──

    async def save_captcha(self, chat_id: int, user_id: int, answer: str, created_at: float):
        await self._execute(
            "INSERT OR REPLACE INTO captcha (chat_id, user_id, answer, created_at) VALUES (?, ?, ?, ?)",
            [chat_id, user_id, answer, created_at]
        )

    async def get_captcha(self, chat_id: int, user_id: int):
        row = await self._fetchone(
            "SELECT answer, created_at FROM captcha WHERE chat_id=? AND user_id=?",
            [chat_id, user_id]
        )
        return row

    async def delete_captcha(self, chat_id: int, user_id: int):
        await self._execute(
            "DELETE FROM captcha WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )

    # ── Polls ──

    async def create_poll(self, chat_id: int, poll_id: str, question: str, options: list):
        await self._execute(
            "INSERT INTO polls (chat_id, poll_id, question, options, votes) VALUES (?, ?, ?, ?, ?)",
            [chat_id, poll_id, question, json.dumps(options), json.dumps({})]
        )

    async def vote_poll(self, chat_id: int, poll_id: str, option_idx: int, user_id: int):
        row = await self._fetchone(
            "SELECT options, votes, is_open FROM polls WHERE chat_id=? AND poll_id=?",
            [chat_id, poll_id]
        )
        if not row or not row["is_open"]:
            return None
        votes = json.loads(row["votes"])
        if str(user_id) in votes:
            return False
        votes[str(user_id)] = option_idx
        await self._execute(
            "UPDATE polls SET votes=? WHERE chat_id=? AND poll_id=?",
            [json.dumps(votes), chat_id, poll_id]
        )
        return True

    async def close_poll(self, chat_id: int, poll_id: str):
        await self._execute(
            "UPDATE polls SET is_open=0 WHERE chat_id=? AND poll_id=?", [chat_id, poll_id]
        )

    async def get_poll(self, chat_id: int, poll_id: str):
        row = await self._fetchone(
            "SELECT * FROM polls WHERE chat_id=? AND poll_id=?", [chat_id, poll_id]
        )
        if row:
            row["options"] = json.loads(row["options"])
            row["votes"] = json.loads(row["votes"])
        return row

    # ── Daily claim ──

    async def get_last_daily(self, user_id: int, chat_id: int) -> str:
        row = await self._fetchone(
            "SELECT last_claim FROM daily_claims WHERE user_id=? AND chat_id=?", [user_id, chat_id]
        )
        return row["last_claim"] if row else ""

    async def set_last_daily(self, user_id: int, chat_id: int, date_str: str):
        await self._execute(
            "INSERT OR REPLACE INTO daily_claims (user_id, chat_id, last_claim) VALUES (?, ?, ?)",
            [user_id, chat_id, date_str]
        )

    # ── Activation ──

    async def is_group_active(self, chat_id: int) -> bool:
        row = await self._fetchone("SELECT is_active FROM groups WHERE chat_id=?", [chat_id])
        return bool(row["is_active"]) if row else False

    async def activate_group(self, chat_id: int, activated_by: int, owner_id: int, time_str: str):
        await self.ensure_group(chat_id)
        await self._execute(
            "UPDATE groups SET is_active=1, activated_by=?, activated_at=?, owner_id=? WHERE chat_id=?",
            [activated_by, time_str, owner_id, chat_id]
        )

    async def deactivate_group(self, chat_id: int):
        await self._execute("UPDATE groups SET is_active=0 WHERE chat_id=?", [chat_id])

    async def get_owner(self, chat_id: int) -> int:
        row = await self._fetchone("SELECT owner_id FROM groups WHERE chat_id=?", [chat_id])
        return row["owner_id"] if row else 0

    async def get_activation_info(self, chat_id: int):
        row = await self._fetchone(
            "SELECT is_active, activated_by, activated_at, owner_id FROM groups WHERE chat_id=?",
            [chat_id]
        )
        return row

    # ── Night mode ──

    async def get_night_mode(self, chat_id: int) -> dict:
        row = await self._fetchone(
            "SELECT night_mode, night_start, night_end FROM groups WHERE chat_id=?", [chat_id]
        )
        if row:
            return {"enabled": bool(row["night_mode"]), "start": row["night_start"], "end": row["night_end"]}
        return {"enabled": False, "start": 22, "end": 7}

    async def set_night_mode(self, chat_id: int, enabled: bool, start: int = None, end: int = None):
        await self.ensure_group(chat_id)
        if start is not None and end is not None:
            await self._execute("UPDATE groups SET night_mode=?, night_start=?, night_end=? WHERE chat_id=?", [1 if enabled else 0, start, end, chat_id])
        else:
            await self._execute("UPDATE groups SET night_mode=? WHERE chat_id=?", [1 if enabled else 0, chat_id])

    async def set_night_hours(self, chat_id: int, start: int, end: int):
        await self.ensure_group(chat_id)
        await self._execute("UPDATE groups SET night_start=?, night_end=? WHERE chat_id=?", [start, end, chat_id])

    # ── Group admins tracking ──

    async def track_admin(self, chat_id: int, user_id: int):
        await self.ensure_member(chat_id, user_id)
        await self._execute(
            "UPDATE members SET is_admin=1 WHERE chat_id=? AND user_id=?", [chat_id, user_id]
        )

    async def get_user_admin_groups(self, user_id: int) -> list:
        rows = await self._fetchall(
            "SELECT g.chat_id, g.title, g.is_active FROM groups g "
            "INNER JOIN members m ON g.chat_id=m.chat_id "
            "WHERE m.user_id=? AND m.is_admin=1",
            [user_id]
        )
        return rows

    async def get_group_title(self, chat_id: int) -> str:
        row = await self._fetchone("SELECT title FROM groups WHERE chat_id=?", [chat_id])
        return row["title"] if row else ""

    # ── Export / Import ──

    async def export_group(self, chat_id: int) -> dict:
        group = await self._fetchone("SELECT * FROM groups WHERE chat_id=?", [chat_id])
        if not group:
            return {}
        replies = await self.get_custom_replies(chat_id)
        words = await self.get_bad_words(chat_id)
        return {"settings": dict(group), "replies": replies, "bad_words": words}

    async def import_group(self, chat_id: int, data: dict):
        settings = data.get("settings", {})
        if settings:
            await self.ensure_group(chat_id)
            for key, val in settings.items():
                if key != "chat_id":
                    try:
                        await self.set_setting(chat_id, key, val)
                    except Exception:
                        pass
        for kw, reply in data.get("replies", {}).items():
            await self.add_custom_reply(chat_id, kw, reply)
        for word in data.get("bad_words", []):
            await self.add_bad_word(chat_id, word)


    # ── Leveling & XP ──

    async def add_xp(self, chat_id: int, user_id: int, amount: int = 1):
        await self.ensure_member(chat_id, user_id)
        row = await self._fetchone("SELECT xp, level FROM members WHERE chat_id=? AND user_id=?", [chat_id, user_id])
        if not row: return False
        
        new_xp = row["xp"] + amount
        new_level = row["level"]
        level_up = False
        
        # Simple curve: level * 50
        req_xp = new_level * 50
        if new_xp >= req_xp:
            new_level += 1
            new_xp = 0
            level_up = True
            
        await self._execute(
            "UPDATE members SET xp=?, level=? WHERE chat_id=? AND user_id=?", 
            [new_xp, new_level, chat_id, user_id]
        )
        return level_up, new_level

    async def get_top_levels(self, chat_id: int, limit: int = 10):
        return await self._fetchall(
            "SELECT user_id, level, xp FROM members WHERE chat_id=? ORDER BY level DESC, xp DESC LIMIT ?", 
            [chat_id, limit]
        )

    # ── Marriages ──

    async def get_marriage(self, user_id: int):
        row = await self._fetchone(
            "SELECT * FROM marriages WHERE user1_id=? OR user2_id=?", 
            [user_id, user_id]
        )
        return row

    async def marry(self, user1: int, user2: int, date_str: str):
        await self._execute(
            "INSERT INTO marriages (user1_id, user2_id, marriage_date) VALUES (?, ?, ?)",
            [user1, user2, date_str]
        )

    async def divorce(self, user_id: int):
        await self._execute(
            "DELETE FROM marriages WHERE user1_id=? OR user2_id=?", 
            [user_id, user_id]
        )

    # ── Clans ──

    async def get_clan_by_name(self, name: str):
        return await self._fetchone("SELECT * FROM clans WHERE name=?", [name])

    async def create_clan(self, name: str, owner_id: int, created_at: str):
        cur = await self._execute(
            "INSERT INTO clans (name, owner_id, created_at) VALUES (?, ?, ?)",
            [name, owner_id, created_at]
        )
        await self._execute("INSERT INTO clan_members (clan_id, user_id) VALUES (?, ?)", [cur.lastrowid, owner_id])
        return cur.lastrowid

    async def get_user_clan(self, user_id: int):
        row = await self._fetchone(
            "SELECT c.* FROM clans c INNER JOIN clan_members m ON c.clan_id=m.clan_id WHERE m.user_id=?", 
            [user_id]
        )
        return row

    async def get_top_clans(self, limit: int = 10):
        return await self._fetchall("SELECT * FROM clans ORDER BY xp DESC, balance DESC LIMIT ?", [limit])

    # ── Broadcast Users & Groups ──
    async def get_all_active_groups(self):
        return await self._fetchall("SELECT chat_id FROM groups WHERE is_active=1")

    async def get_all_private_users(self):
        return await self._fetchall("SELECT DISTINCT user_id FROM members")

    # ── Global bot users ──
    
    async def track_user(self, user_id: int, username: str, full_name: str):
        from utils.helpers import format_date
        now = format_date()
        await self._execute(
            "INSERT OR IGNORE INTO bot_users (user_id, username, full_name, join_date) VALUES (?, ?, ?, ?)",
            [user_id, username or "", full_name or "عضو", now]
        )
        
    async def get_all_private_users(self):
        return await self._fetchall("SELECT user_id FROM bot_users")
        
    async def get_all_active_groups(self):
        return await self._fetchall("SELECT chat_id FROM groups WHERE is_active=1")

    async def get_bot_stats(self):
        users = await self._fetchone("SELECT COUNT(*) as count FROM bot_users")
        groups = await self._fetchone("SELECT COUNT(*) as count FROM groups")
        active_groups = await self._fetchone("SELECT COUNT(*) as count FROM groups WHERE is_active=1")
        return {
            "users": users["count"] if users else 0,
            "groups": groups["count"] if groups else 0,
            "active_groups": active_groups["count"] if active_groups else 0
        }

db = Database()
