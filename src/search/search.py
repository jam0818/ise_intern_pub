# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 11:12:11 2023

@author: pinyo
"""

import json
import os
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List


class TextAnalyzer:
    def __init__(self, data_path: str, save_path: str, target_dir: str, threshold: float = 0.8):
        self.data_path = data_path
        self.save_path = save_path
        self.threshold = threshold
        self.target_dir = target_dir
        self.config = {
            "GOOGLE_API_KEY": os.environ["GOOGLE_API_KEY"],
            "CUSTOM_SEARCH_ENGINE_ID": os.environ["CUSTOM_SEARCH_ENGINE_ID"],
        }

    @staticmethod
    def extract_nouns(text, lang):
        try:
            if lang == 'ja':
                nlp = spacy.load('ja_ginza')  # 日本語のモデル
            else:
                nlp = spacy.load('en_core_web_sm')  # 英語のモデル
        except Exception as e:
            print(f"Error in NLP processing: {str(e)}")
            return []

        doc = nlp(text)
        nouns = [chunk.text for chunk in doc.noun_chunks]  # 名詞句を抽出
        # print(nouns)
        return nouns

    def get_search_results(self, keyword, number=3):
        try:
            params = {
                "key": self.config["GOOGLE_API_KEY"],
                "cx": self.config["CUSTOM_SEARCH_ENGINE_ID"],
                "q": keyword,
                "num": number
            }
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            response.raise_for_status()
            search_results = response.json()

            results = []
            for item in search_results.get("items", []):
                title = item.get("title")
                link = item.get("link")
                results.append({"keyword": keyword, "title": title, "url": link})
            return results

        except requests.RequestException as e:
            print(f"Error during requests to Google Custom Search API: {str(e)}")
            return []

    def analyze_text(self, file_name: str, lang) -> List[dict]:
        try:
            with open(os.path.join(self.data_path, self.target_dir, file_name), 'r', encoding='utf-8') as file:
                data = json.load(file)
                # キー変更する
                text = data['text']
        except FileNotFoundError:
            raise FileNotFoundError(f"File {file_name} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {file_name}")

        nouns = self.extract_nouns(text, lang)
        # TF-IDFを使用して単語の重要度を計算
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([' '.join(nouns)])
        tfidf_scores = {word: tfidf_matrix[0, idx] for word, idx in vectorizer.vocabulary_.items()}

        # TF-IDFスコアに基づいて単語をソートし、上位を選択
        sorted_nouns = sorted(tfidf_scores.items(), key=lambda item: item[1], reverse=True)[:3]
        """
        print("Top 3 TF-IDF Scores:")
        for noun, score in sorted_nouns:
            print(f"{noun}: {score}")
        """

        selected_nouns = [noun for noun, score in sorted_nouns]
        search_results = []
        for noun in selected_nouns:
            search_results.extend(self.get_search_results(noun))

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        if not os.path.exists(os.path.join(self.save_path, self.target_dir)):
            os.makedirs(os.path.join(self.save_path, self.target_dir))

        with open(os.path.join(self.save_path, self.target_dir, "search_result.json"), "w") as f:
            json.dump(search_results, f, ensure_ascii=False)

        return search_results


if __name__ == '__main__':
    analyzer = TextAnalyzer("./data/summarized", "./data/searched/", "dummy")
    analyzer.analyze_text("summarized.json", lang='ja')
