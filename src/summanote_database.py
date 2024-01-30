from datetime import datetime
import sys
import os
from src import db


class Summanote_database:
    def __init__(self):
        self.db = db.Database('summanote.db')
        self.db.create_connection()
        self.db.create_table("""
            CREATE TABLE IF NOT EXISTS summanote (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT UNIQUE, 
            note_path TEXT UNIQUE, 
            transcribed_text TEXT,
            revised_text TEXT,
            summarized_text TEXT,
            searched_info TEXT,
            created_at TEXT, 
            updated_at TEXT)
        """)

    def insert_data(self, title, note_path) -> None:
        """

        :param title:
        :param note_path:
        :return:
        """
        transcribed_text = ''
        revised_text = ''
        summarized_text = ''
        searched_info = ''
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (title,
                note_path,
                transcribed_text,
                revised_text,
                summarized_text,
                searched_info,
                created_at,
                updated_at)
        self.db.insert_data('summanote', data)

    def select_all_data(self) -> list:
        """

        :return:
        """
        return self.db.select_all_data('summanote')

    def select_single_data(self, column, value) -> tuple:
        """

        :param column:
        :param value:
        :return:
        """
        return self.db.select_single_data('summanote', column, value)

    def update_data(self, set_column, set_value, where_column, where_value) -> None:
        """

        :param set_column:
        :param set_value:
        :param where_column:
        :param where_value:
        :return:
        """
        if set_column == 'updated_at':
            set_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.update_data('summanote', set_column, set_value, where_column, where_value)

    def delete_data(self, where_column, where_value) -> None:
        """

        :param where_column:
        :param where_value:
        :return:
        """
        self.db.delete_data('summanote', where_column, where_value)

