import sqlite3
from sqlite3 import Error
import os
import logging

from src.custom_logging import CustomHandler

# ロガーの作成
logger = logging.getLogger('db_logger')

# ログレベルの設定
logger.setLevel(logging.DEBUG)

# ファイルハンドラの作成
file_handler = CustomHandler('logs/db.log')

# ログフォーマットの作成
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ファイルハンドラにフォーマットを設定
file_handler.setFormatter(formatter)

# ロガーにファイルハンドラを追加
logger.addHandler(file_handler)


class Database:
    def __init__(self, db_file):
        self.conn = None
        self.db_file = os.path.join(os.getenv('DATABASE_PATH'), db_file)

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            logger.info('Database connection established.')
        except Error as e:
            logger.error('Failed to establish database connection.', exc_info=True)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            logger.info('Database connection closed.')

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
            logger.info('Table created.')
        except Error as e:
            logger.error('Failed to create table.', exc_info=True)

    def drop_table(self, table):
        try:
            c = self.conn.cursor()
            c.execute(f"DROP TABLE {table}")
            logger.info('Table dropped.')
        except Error as e:
            logger.error('Failed to drop table.', exc_info=True)

    def insert_data(self, table, data):
        try:
            with self.conn:
                c = self.conn.cursor()
                placeholders = ', '.join(['?'] * len(data))
                c.execute(f"INSERT INTO {table} VALUES (NULL, {placeholders})", data)
                logger.info('Data inserted.')
        except Error as e:
            logger.error('Failed to insert data.', exc_info=True)

    def select_single_data(self, table, column, value):
        try:
            with self.conn:
                c = self.conn.cursor()
                c.execute(f"SELECT * FROM {table} WHERE {column} = ?", (value,))
                logger.info(f'Selected data from {table} where {column} = {value}.')
                return c.fetchone()
        except Error as e:
            logger.error('Failed to select data.', exc_info=True)

    def select_all_data(self, table):
        try:
            with self.conn:
                c = self.conn.cursor()
                c.execute(f"SELECT * FROM {table}")
                logger.info('Data selected.')
                return c.fetchall()
        except Error as e:
            logger.error('Failed to select data.', exc_info=True)

    def update_data(self, table, set_column, set_value, where_column, where_value):
        try:
            with self.conn:
                c = self.conn.cursor()
                c.execute(f"UPDATE {table} SET {set_column} = ? WHERE {where_column} = ?", (set_value, where_value))
                logger.info('Data updated.')
        except Error as e:
            logger.error('Failed to update data.', exc_info=True)

    def delete_data(self, table, where_column, where_value):
        try:
            with self.conn:
                c = self.conn.cursor()
                c.execute(f"DELETE FROM {table} WHERE {where_column} = ?", (where_value,))
                logger.info('Data deleted.')
        except Error as e:
            logger.error('Failed to delete data.', exc_info=True)
