from src.convocollect_execution_classes import Translator
from src.convocollect_database import ConvoCollectDatabase
from src.summanote_database import Summanote_database


class ConvoCollectPipeline:
    def __init__(self):
        self.translator = Translator('ja')
        self.cc_db = ConvoCollectDatabase()
        self.sn_db = Summanote_database()

    def translate(self, text):
        return self.translator.translate(text)
