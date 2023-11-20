# import文
import os
import logging
import queue
import json
import random
from dotenv import load_dotenv

from flask import (
    Flask,
    request,
    render_template,
    Response,
    send_file
)

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import (
    RedisChatMessageHistory,
    ConversationBufferMemory
)

from add_document import initialize_vectorstore
from modules.callbacks import MyCustomCallbackHandler
from modules.debugger import inner_log

# 内部処理確認の有無
inner_log(False)

# 環境変数の読み込み
load_dotenv()

# Flaskアプリの初期化
app = Flask(__name__)

# ストーリミング形式の応答を順番に格納するためのキューの準備
que = queue.Queue()
# デフォルトのsession_id
session_id = "defauly-session"
# Vector storeの読み込み
vectorstore = initialize_vectorstore()


# ルートエンドポイント
@app.route('/')
def index():
    # ページがリロードされるたびにsession_idを更新する
    global session_id
    session_id = str(random.uniform(1, 100))
    logger.info("session_id:" + session_id)
    return render_template('index.html')


# ボットアイコン表示用エンドポイント
@app.route('/icon/boticon')
def icon():
    # アイコン画像の取得
    icon = os.path.dirname(__file__) + '/' + 'templates/boticon.png'
    logger.info("icon:" + icon)
    # アイコンをWebサーバにダウンロード
    return send_file(icon, mimetype='image/png')


# 回答作成用エンドポイント
@app.route('/ask')
def ask():
    # Redisに会話履歴を保存するための準備
    history = RedisChatMessageHistory(
        url="redis://localhost:6379/0",
        ttl=600,
        session_id=session_id
    )

    # 最初の質問内容を保存するためのメモリ
    memory = ConversationBufferMemory(
        chat_memory=history,
        memory_key="chat_history",
        return_messages=True
    )

    global que

    # Language modelsの初期化(質問生成用)
    llm = ChatOpenAI(
        model=os.environ["OPENAI_API_MODEL"],
        temperature=os.environ["OPENAI_API_TEMPERATURE"],
        streaming=True,
        callbacks=[MyCustomCallbackHandler(que)]
    )

    # 最終的な応答を取得するためのLanguage models
    condense_question_llm = ChatOpenAI(
        model=os.environ["OPENAI_API_MODEL"],
        temperature=os.environ["OPENAI_API_TEMPERATURE"],
    )

    # Chainの設定
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        condense_question_llm=condense_question_llm
    )

    # リクエストのJSONボディからデータを取得
    message = request.args.get('text')
    callback = request.args.get('callback')

    # 回答の取得
    answer = qa_chain.run(message)

    logger.info("answer:" + answer)

    # クライアントへのレスポンスを作成
    res = callback + '(' + json.dumps({
            "output": [
                {
                    "type": "text",
                    "value": answer
                }
                ]
        }) + ')'
    logger.info("res:" + res)

    return res


# SSE用エンドポイント
@app.route('/listen')
def listen():
    def stream():
        while True:
            msg = que.get()
            if msg is None:
                break
            yield f'data: {msg}\n\n'
    response = Response(stream(), mimetype='text/event-stream')
    return response


if __name__ == '__main__':

    # ロガーの初期化
    # フォーマットとログレベルの設定
    logging.basicConfig(
        format="%(asctime)s %(message)s", level=logging.INFO
        )
    # ロガーの作成
    logger = logging.getLogger(__name__)

    app.run(debug=True, port=5001, threaded=True)
