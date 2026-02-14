import sqlite3
from typing import Optional, List


class Database:
    def __init__(self, db_path: str = "bot_database.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        #self.conn.row_factory = lambda cursor, row: row[0]
        self.cursor = self.conn.cursor()

    # =========================
    # СОЗДАНИЕ ТАБЛИЦ
    # =========================

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            nickname TEXT,
            chat_id INTEGER,
            stats TEXT,
            current_chat INTEGER,
            searching INTEGER DEFAULT 0
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER,
            user2_id INTEGER,
            anonymous INTEGER DEFAULT 1,
            active INTEGER DEFAULT 1,
            history TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            sender_id INTEGER,
            text TEXT,
            type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    # =========================
    # USERS
    # =========================

    def create_user(
        self,
        user_id: int,
        nickname: str,
        chat_id: int,
        stats: str
    ):
        self.cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, nickname, chat_id, stats, current_chat, searching)
        VALUES (?, ?, ?, ?, NULL, 0)
        """, (user_id, nickname, chat_id, stats))
        self.conn.commit()

    def update_user(
        self,
        user_id: int,
        nickname: str,
        chat_id: int,
        stats: str,
        current_chat: Optional[int],
        searching: int
    ):
        self.cursor.execute("""
        UPDATE users SET
            nickname = ?,
            chat_id = ?,
            stats = ?,
            current_chat = ?,
            searching = ?
        WHERE user_id = ?
        """, (nickname, chat_id, stats, current_chat, searching, user_id))
        self.conn.commit()

    def get_user(self, user_id: int) -> Optional[sqlite3.Row]:
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        return self.cursor.fetchone()
    
    def get_user_by_id(self, id: int) -> Optional[sqlite3.Row]:
        self.cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (id,)
        )
        return self.cursor.fetchone()
        

    def get_user_by_nickname(self, nickname: str) -> Optional[sqlite3.Row]:
        self.cursor.execute(
            "SELECT * FROM users WHERE nickname = ?",
            (nickname,)
        )
        return self.cursor.fetchone()

    # =========================
    # CHATS
    # =========================

    def create_chat(
        self,
        user1_id: int,
        user2_id: int,
        anonymous: int = 1,
        active: int = 1
    ) -> int:
        self.cursor.execute("""
        INSERT INTO chats (user1_id, user2_id, anonymous, active, history)
        VALUES (?, ?, ?, ?, ?)
        """, (user1_id, user2_id, anonymous, active, "[]"))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_chat(
        self,
        chat_id: int,
        user1_id: int,
        user2_id: int,
        anonymous: int,
        active: int,
        history: str
    ):
        self.cursor.execute("""
        UPDATE chats SET
            user1_id = ?,
            user2_id = ?,
            anonymous = ?,
            active = ?,
            history = ?
        WHERE id = ?
        """, (user1_id, user2_id, anonymous, active, history, chat_id))
        self.conn.commit()

    def get_chat(self, chat_id: int) -> Optional[sqlite3.Row]:
        self.cursor.execute(
            "SELECT * FROM chats WHERE id = ?",
            (chat_id,)
        )
        return self.cursor.fetchone()
    
    def get_chat_by_id(self, chat_id: int) -> Optional[sqlite3.Row]:
        self.cursor.execute(
            "SELECT * FROM chats WHERE id = ?",
            (chat_id,)
        )
        return self.cursor.fetchone()

    def get_user_chats(self, user_id: int) -> List[sqlite3.Row]:
        """
        Все чаты, где участвует пользователь
        """
        self.cursor.execute("""
        SELECT * FROM chats
        WHERE user1_id = ? OR user2_id = ?
        """, (user_id, user_id))
        return self.cursor.fetchall()

    # =========================
    # MESSAGES
    # =========================

    def add_message(self, chat_id: int, sender_id: int, text: str):
        self.cursor.execute("""
        INSERT INTO messages (chat_id, sender_id, text)
        VALUES (?, ?, ?)
        """, (chat_id, sender_id, text))
        self.conn.commit()

    def get_chat_messages(
        self,
        chat_id: int,
        limit: int = 50
    ) -> List[sqlite3.Row]:
        self.cursor.execute("""
        SELECT * FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (chat_id, limit))
        return self.cursor.fetchall()

    def get_all_chat_messages(self, chat_id: int) -> List[sqlite3.Row]:
        """
        ВСЕ сообщения чата без лимита
        """
        self.cursor.execute("""
        SELECT * FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
        """, (chat_id,))
        return self.cursor.fetchall()

    # =========================
    # SERVICE
    # =========================

    def close(self):
        self.conn.close()
