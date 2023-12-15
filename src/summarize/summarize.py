from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

import os
import json


class Summarizer:
    def __init__(self, data_path: str, save_path: str, target_dir: str):
        self.data_path = data_path
        self.save_path = save_path
        self.target_dir = target_dir
        self.summarized_text = ""

    def summarize(self, file_name: str, prompt: str = "以下の内容を短く要約して下さい。"):
        with open(os.path.join(self.data_path, self.target_dir, file_name), 'r') as f:
            d = json.load(f)
            text = d["text"]

        map_prompt_template = """以下の文章の概要をまとめて下さい。
        ------
        {text}
        ------
        """

        map_combine_template = prompt + """
        ------
        {text}
        ------
        """

        map_first_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
        map_combine_prompt = PromptTemplate(template=map_combine_template, input_variables=["text"])

        map_chain = load_summarize_chain(
            llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
            reduce_llm=ChatOpenAI(temperature=0, model_name="gpt-4"),
            collapse_llm=ChatOpenAI(temperature=0, model_name="gpt-4"),
            chain_type="map_reduce",
            map_prompt=map_first_prompt,
            combine_prompt=map_combine_prompt,
            collapse_prompt=map_combine_prompt,
            token_max=5000,
            verbose=True
        )

        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0, separator="\n"
        )
        texts = text_splitter.split_text(text)

        docs = [Document(page_content=t) for t in texts]
        result = map_chain({"input_documents": docs}, return_only_outputs=True)
        self.summarized_text = result["output_text"]

        return self.summarized_text

    def save_text(self, file_name: str):
        if not os.path.exists(os.path.join(self.save_path, self.target_dir)):
            os.makedirs(os.path.join(self.save_path, self.target_dir), exist_ok=True)
        result = {"text": self.summarized_text}
        with open(os.path.join(self.save_path, self.target_dir, file_name), "w") as f:
            json.dump(result, f, ensure_ascii=False)


if __name__ == '__main__':
    summarizer = Summarizer("./data/revised/", "./data/summarized/", "dummy")
    summarizer.summarize("test.json")
    summarizer.save_text("summarized.json")
