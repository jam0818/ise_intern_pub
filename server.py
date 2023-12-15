import logging
import os

import uvicorn
from fastapi import FastAPI, status
from fastapi.datastructures import UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from src.revise.revise import Reviser
from src.search.search import TextAnalyzer
from src.summarize.summarize import Summarizer
from src.transcribe.transcribe import Transcriber

logger = logging.getLogger(__name__)


class FileUpload(BaseModel):
    file: UploadFile


class SelectDir(BaseModel):
    dir: str


ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'wav'}
transcriber = Transcriber(data_path="./data/recorded",
                          save_path="./data/transcribed",
                          target_dir="dummy",
                          config={"model_name": "small", "device": "cuda:0"})
transcriber.make_model()
reviser = Reviser(data_path="./data/transcribed",
                  save_path="./data/revised",
                  target_dir="dummy")
summarizer = Summarizer(data_path="./data/revised",
                        save_path="./data/summarized",
                        target_dir="dummy")
searcher = TextAnalyzer(data_path="./data/summarized",
                        save_path="./data/searched",
                        target_dir="dummy")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./static", html=True), name="static")


@app.get("/")
async def root():
    """
    ルートディレクトリにアクセスしたときに返す
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "OK"}
    )


@app.get("/api/get_dir_list")
async def get_dir_list() -> JSONResponse:
    """
    音声ファイルが保存されているディレクトリのリストを返す
    :return: JSONResponse
    """
    try:
        if not os.path.exists(transcriber.data_path):
            os.mkdir(transcriber.data_path)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"dir_list": os.listdir(transcriber.data_path)}
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.get("/api/start_recording")
async def start_recording():
    """
    録音を開始する
    :return: JSONResponse
    """
    try:
        if len(os.listdir(os.path.join(transcriber.data_path, transcriber.target_dir))) > 0:
            # target_dir にファイルが存在する場合は削除する
            for file_name in os.listdir(os.path.join(transcriber.data_path, transcriber.target_dir)):
                os.remove(os.path.join(transcriber.data_path, transcriber.target_dir, file_name))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "OK"}
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.get("/api/summarize")
async def summarize():
    """
    書き起こしたテキストを要約する
    :return: JSONResponse  要約されたテキスト
    """
    try:
        transcriber.integrate_texts()
        revised_text = reviser.revise("integrated.json")
        summarized_text = summarizer.summarize("revised_integrated.json")
        summarizer.save_text("summarized.json")
        # revised_text = {"text": "revised text"}
        # summarized_text = {"text": "summarized text"}
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "revised_text": revised_text,
                "summarized_text": summarized_text
            }
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.get("/api/load_all_text")
async def load_all_text():
    """
    書き起こしたテキストを全て読み込む
    :return:
    """
    try:
        # todo: ファイルの読み込みでtext 定義ができるようにする
        text = "transcribed text"
        revised_text = "revised text"
        summarized_text = "summarized text"
        content = {
            "text": text,
            "revised_text": revised_text,
            "summarized_text": summarized_text
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=content
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.get("/api/get_useful_info")
async def get_useful_info():
    """
    有益な情報のリストdict形式で返す
    :return: JSONResponse
    """
    try:
        content = searcher.analyze_text("summarized.json", lang='ja')
        useful_info = {
            "useful_info": content
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=useful_info
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.post("/api/create_dir")
async def create_dir(request: SelectDir, status_code=status.HTTP_200_OK):
    """
    音声ファイルを保存するディレクトリを作成する
    :param request: SelectDir  リクエスト
    :param status_code: int  ステータスコード
    :return: JSONResponse
    """
    try:
        dir_name = request.dir
        if not os.path.exists(os.path.join(transcriber.data_path, dir_name)):
            os.mkdir(os.path.join(transcriber.data_path, dir_name))
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Already exists"}
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "OK"}
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.post("/api/transcribe")
async def transcribe(request: Request, status_code=status.HTTP_200_OK):
    """
    音声ファイルを受け取り、書き起こしを行う
    :param request: Request  リクエスト
    :param status_code: int  ステータスコード
    :return: JSONResponse
    """
    try:
        form_data = await request.form()
        uploaded_file = form_data['file']

        # ファイルをサーバー上に保存
        file_name = uploaded_file.filename
        file_path = os.path.join(transcriber.data_path, transcriber.target_dir, file_name)

        with open(file_path, "wb") as file:
            file.write(uploaded_file.file.read())

        # レスポンスに保存したファイルのパスを含めることもできます
        file_info = {
            "filename": file_name,
            "content_type": uploaded_file.content_type,
            "file_size": len(uploaded_file.file.read()),
            "saved_path": file_path  # ファイルの保存パス
        }

        text = transcriber.save_text(file_name=file_name)
        # todo: リアルタイムで校正する場合revised text も変数として定義する
        # revised_text = reviser.revise(text) みたいな感じで実装

        # WAVファイルの処理を行うことができます
        # この例ではファイルを受け取り、その情報をJSONレスポンスで返します
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"text": text}
        )
        # return JSONResponse(status_code=status.HTTP_200_OK, content={"text": text, "revised_text": revised_text})

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.post("/api/set_dir")
async def set_dir(request: SelectDir, status_code=status.HTTP_200_OK):
    """
    音声ファイルが保存されているディレクトリを設定する
    :param request: Request  リクエスト
    :param status_code: int  ステータスコード
    :return: JSONResponse
    """
    try:
        target_dir = request.dir
        transcriber.target_dir = target_dir
        reviser.target_dir = target_dir
        summarizer.target_dir = target_dir
        searcher.target_dir = target_dir
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "OK"}
        )

    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    """
    バリデーションエラーが発生したときに返す
    :param request: Request
    :param exc: RequestValidationError
    :return: JSONResponse
    """
    logger.error(exc)
    return JSONResponse(
        content={},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


if __name__ == '__main__':
    print(os.environ["OPENAI_API_KEY"])
    logging.basicConfig(filename='api.log', level=logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
