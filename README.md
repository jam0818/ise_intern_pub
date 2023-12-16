# ise_intern

これは動作に正しく設定された特定の環境変数の設定を必要とするシンプルなPythonサーバーアプリケーションです。以下の手順に従ってアプリケーションをセットアップし、実行します。

## 前提条件

アプリケーションを実行する前に、以下の前提条件がインストールされていることを確認してください：

- Python
- Poetry（依存関係管理のため）

## セットアップ

1. リポジトリをローカルマシンにクローンします：

   ```bash
   git clone git@github.com:jam0818/ise_intern_pub.git
   cd ise_intern_pub
   ```
2. Poetryを使用してプロジェクトの依存関係をインストールします：
   ```bash
   poetry install
   ```
3. 次の環境変数を設定してください：
   ```bash
   OPENAI_API_KEY=xxx
   CUSTOM_SEARCH_ENGINE_ID=xxx
   GOOGLE_API_KEY=xxx
   ```
4. 実行
   ```bash
   poetry run python server.py
   ```

# ディレクトリ構造
```
.
├── data
│   ├── recorded  # 録音音声
│   ├── revised  # 校正後テキスト
│   ├── searched  # 検索結果
│   ├── summarized  # 要約後テキスト
│   └── transcribed  # 書きおこしテキスト
├── src
│   ├── revise  # 校正用のclass
│   ├── search  # 文献検索用のclass
│   ├── summarize  # 要約用のclass
│   └── transcribe  # 書きおこし用のクラス
├── static  # フロントエンド
└── server.py  # バックエンド
```
