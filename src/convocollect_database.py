from src.db import Database
from datetime import datetime


class ConvoCollectDatabase:
    def __init__(self):
        self.db = Database('convocollect.db')
        self.db.create_connection()
        self.db.create_table("""
            CREATE TABLE IF NOT EXISTS convocollect (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            word TEXT UNIQUE, 
            frequency INTEGER, 
            ex_texts TEXT,
            created_at TEXT, 
            updated_at TEXT
            )
        """)

    def insert_data(self, word) -> None:
        """

        :param word:
        :param frequency:
        :param ex_texts:
        :return:
        """
        frequency = 1
        ex_texts = ''
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (word,
                frequency,
                ex_texts,
                created_at,
                updated_at)
        self.db.insert_data('convocollect', data)
