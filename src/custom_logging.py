import logging
import os


class CustomHandler(logging.FileHandler):
    def emit(self, record):
        # ログメッセージをファイルに書き込む前に行数をチェック
        if self.should_trim_file():
            self.trim_file()
        logging.FileHandler.emit(self, record)

    def should_trim_file(self):
        # ファイルが存在しない場合はトリム不要
        if not os.path.exists(self.baseFilename):
            return False
        # ファイルの行数をチェック
        with open(self.baseFilename, 'r') as f:
            lines = f.readlines()
        return len(lines) > 1000

    def trim_file(self):
        # ファイルの行数が1000行を超えていたら、最新の1000行だけを残す
        with open(self.baseFilename, 'r') as f:
            lines = f.readlines()
        with open(self.baseFilename, 'w') as f:
            f.writelines(lines[-1000:])