import os
import requests


class Translator:
    def __init__(self, language):
        self.language = language
        self.api_key = os.environ['DEEPL_API_KEY']

    def translate(self, text):
        request = {
            "auth_key": self.api_key,
            "text": text,
            "source_lang": 'JA',
            "target_lang": 'EN'
        }
        response = requests.post('https://api-free.deepl.com/v2/translate', data=request).json()
        return response['translations'][0]['text']





if __name__ == '__main__':
    translator = Translator('ja')
    print(translator.translate('私はペンです'))
