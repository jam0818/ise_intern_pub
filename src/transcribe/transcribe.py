import json
import logging
import os
from datetime import datetime
from typing import List

import whisper
from tqdm import tqdm

logging.basicConfig(filename='transcriber.log', level=logging.INFO)


class Transcriber:
    """
    音声ファイルの書きおこしを行うクラス
    """

    def __init__(
            self,
            data_path: str,
            save_path: str,
            target_dir: str,
            config=None
    ) -> None:
        """
        :param data_path: str
        :param save_path: str
        :param config: dict
        """
        if config is None:
            config = {"model_name": "small", "device": "cuda:0"}
        self.data_path = data_path
        self.save_path = save_path
        self.target_dir = target_dir
        self.model = None
        self.config = config

        self.logger = logging.getLogger('Transcriber')
        self.logger.addHandler(logging.StreamHandler())

    def get_file_name_list(self) -> List[str]:
        """
        data_path/target_dir にあるファイル名のリストを返す

        :return: List[str]
        """
        file_list = os.listdir(os.path.join(self.data_path, self.target_dir))
        return file_list

    def make_model(self) -> None:
        """
        model を定義する

        :return: None | raise error
        モデルの定義に失敗した場合はエラーを返す.
        """
        if self.config["model_name"] in ["small", "medium", "large", "large-v2"]:
            self.model = whisper.load_model(self.config["model_name"], device=self.config["device"])
        else:
            self.logger.error("ModelNotFound")
            raise NameError("ModelNotFound")

    def transcribe(self, file_name: str) -> dict:
        """
        単一音声ファイルの書きおこしを行う

        :param file_name: str
        :return: dict | None
        書きおこし結果の文字列を返す. モデルの定義に失敗した場合はエラーを返す.
        """
        if self.model is not None:
            self.logger.info("Transcribing: " + file_name)
            result = self.model.transcribe(os.path.join(self.data_path, self.target_dir, file_name))
            result["timestamp"] = datetime.now().isoformat()
            return result
        else:
            self.logger.error("ModelNotFound")
            raise NameError("ModelNotFound")

    def transcribe_all(self) -> None:
        """
        data_path/target_dir にある音声ファイルの書きおこしを行う

        :return: None
        """
        self.logger.info("Transcribing all files in " + self.target_dir)
        for file_name in self.get_file_name_list():
            self.save_text(file_name)

    def save_text(self, file_name: str) -> str:
        """
        data_path/target_dir にある音声ファイルの書きおこし結果を保存する

        :param file_name: str
        :return: str
        """
        self.logger.info("Saving text of " + self.target_dir + "/" + file_name)
        record_dir = os.path.join(self.data_path, self.target_dir)
        transcribe_dir = os.path.join(self.save_path, self.target_dir)
        if not os.path.exists(transcribe_dir):
            os.mkdir(transcribe_dir)
        result_dict = self.transcribe(file_name)
        with open(os.path.join(transcribe_dir, file_name.rsplit('.', 1)[0] + ".json"), "w") as f:
            json.dump(result_dict, f, ensure_ascii=False)
        text = result_dict["text"]

        return text

    def integrate_texts(self) -> None:
        """
        data_path/target_dir にある音声ファイルの書きおこし結果を統合する

        :return: None
        """
        self.logger.info("Integrating texts in " + self.target_dir)
        if not os.path.exists(os.path.join(self.save_path, self.target_dir)):
            os.mkdir(os.path.join(self.save_path, self.target_dir))
        text = []
        for file_name in tqdm(self.get_file_name_list()):
            with open(os.path.join(self.save_path, self.target_dir, file_name.rsplit('.', 1)[0] + ".json"), "r") as f:
                data = json.load(f)
                text.append({"timestamp": data["timestamp"], "text": data["text"]})
        text.sort(key=lambda x: x["timestamp"])
        with open(os.path.join(self.save_path, self.target_dir, "integrated.json"), "w") as f:
            json.dump(text, f, ensure_ascii=False)


if __name__ == '__main__':
    transcriber = Transcriber("./data/recorded/",
                              "./data/transcribed",
                              "dummy2",
                              config={"model_name": "large-v2", "device": "cuda:0"})
    transcriber.make_model()
    transcriber.integrate_texts()

