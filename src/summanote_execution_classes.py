import json
import logging
import os
from datetime import datetime
from typing import List

import whisper
from tqdm import tqdm


class SummanoteBaseClass:
    def __init__(self, sub_dir: str) -> None:
        self.data_path = None
        self.sub_dir = sub_dir

    def set_data_path(self, data_path: str) -> None:
        if self.sub_dir is not None:
            self.data_path = os.path.join(data_path, self.sub_dir)
        else:
            raise ValueError('sub_dir is not set.')


class Transcriber(SummanoteBaseClass):
    def __init__(self, config=None):
        super().__init__('transcribed')
        self.data_path = None
        self.model = None
        self.config = config

    def get_file_name_list(self) -> List[str]:
        if self.data_path is None:
            raise ValueError('NoDataPath')
        else:
            file_list = os.listdir(self.data_path)
            return file_list

    def make_model(self) -> None:
        """
        model を定義する

        :return: None | raise error
        モデルの定義に失敗した場合はエラーを返す.
        """
        if self.config["model_name"] in ["small", "medium", "large", "large-v2"]:
            self.model = whisper.load_model(self.config["model_name"],
                                            device=self.config["device"])
        else:
            raise NameError("ModelNotFound")

    def transcribe(self, file_name: str) -> dict:
        """
        単一音声ファイルの書きおこしを行う

        :param file_name: str
        :return: dict | None
        書きおこし結果の文字列を返す. モデルの定義に失敗した場合はエラーを返す.
        """
        if self.model is None:
            raise ValueError('ModelNotFound')
        else:
            result = {
                "text": self.model.transcribe(os.path.join(self.data_path, file_name)),
                "timestamp": datetime.now().isoformat()
            }
            return result

    def transcribe_all(self) -> dict:
        integrated_result = []
        for file_name in self.get_file_name_list():
            result = self.transcribe(file_name)
            integrated_result.append(result)
        integrated_result.sort(key=lambda x: x['timestamp'])

        integrated_text = ''
        for dic in integrated_result:
            integrated_text += dic['text']

        return {'text': integrated_text}


class Reviser(SummanoteBaseClass):
    def __init__(self, config=None):
        super().__init__('revised')

    def revise(self, text):
        return {'text': 'dummy'}


class Summarizer(SummanoteBaseClass):
    def __init__(self, config=None):
        super().__init__('summarized')

    def summarize(self, text) -> dict:
        return {'text': 'dummy'}


class TextAnalyzer(SummanoteBaseClass):
    def __init__(self, config=None):
        super().__init__('searched')

    def analyze(self, text) -> list:
        return [{'url': 'dummy', 'title': 'dummy', 'description': 'dummy'},
                {'url': 'dummy', 'title': 'dummy', 'description': 'dummy'},
                {'url': 'dummy', 'title': 'dummy', 'description': 'dummy'}]
