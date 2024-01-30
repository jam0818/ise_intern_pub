from src.summanote_database import Summanote_database
from src.summanote_execution_classes import SummanoteBaseClass, Transcriber, Reviser, Summarizer, TextAnalyzer
import os


DEFAULT_DATA_PATH = './data'


class SummanotePipeline:
    def __init__(self, root_path: str = DEFAULT_DATA_PATH):
        self.db = Summanote_database()
        self.current_note_name = None
        self.transcriber = Transcriber()
        self.reviser = Reviser()
        self.summarizer = Summarizer()
        self.text_analyzer = TextAnalyzer()
        self.root_path = root_path

    def set_data_path(self, note_name: str):
        note_path = self.db.select_single_data('title', note_name)[2]
        if note_path is not None:
            self.current_note_name = note_name
            self.transcriber.set_data_path(note_path)
            self.reviser.set_data_path(note_path)
            self.summarizer.set_data_path(note_path)
            self.text_analyzer.set_data_path(note_path)
        else:
            raise ValueError('NoteNotFound')

    def create_new_note(self, note_name: str):
        try:
            note_path = os.path.join(self.root_path, note_name)
            self.db.insert_data(note_name, note_path)
            if not os.path.exists(self.root_path):
                os.mkdir(os.path.join(self.root_path, note_name))
        except Exception as e:
            print(e)

    def transcribe(self, note_name) -> dict:
        # text_acquired_now = self.transcriber.transcribe(note_name)
        text_acquired_now = {'text': 'dummy'}
        past_text = self.db.select_single_data('title', self.current_note_name)[3]
        text_for_update = past_text + text_acquired_now['text']
        self.db.update_data('transcribed_text', text_for_update,
                            'title', self.current_note_name)

        return text_acquired_now

    def revise(self, note_name) -> dict:
        text_acquired_now = self.reviser.revise(self.current_note_name)
        text_for_update = text_acquired_now['text']
        self.db.update_data('revised_text', text_for_update,
                            'title', self.current_note_name)

        return text_acquired_now

    def summarize(self, note_name) -> dict:
        text_acquired_now = self.summarizer.summarize(self.current_note_name)
        text_for_update = text_acquired_now['text']
        self.db.update_data('summarized_text', text_for_update,
                            'title', self.current_note_name)

        return text_acquired_now

    def analyze(self, note_name) -> list:
        text_acquired_now = self.text_analyzer.analyze(self.current_note_name)
        text_for_update = str(text_acquired_now)
        self.db.update_data('searched_info', text_for_update,
                            'title', self.current_note_name)

        return text_acquired_now


if __name__ == '__main__':
    pipeline = summanote_pipeline()
    print('test')
