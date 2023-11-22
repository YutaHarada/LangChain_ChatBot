# import文
import os
import queue
import json
import random

from flask import (
    Blueprint,
    request,
    render_template,
    Response,
    send_file
)

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import (
    CosmosDBChatMessageHistory,
    ConversationBufferMemory
)

from apps.app import logger
from apps.add_document import initialize_vectorstore
from apps.chat.callbacks import MyCustomCallbackHandler


# chatアプリの生成
chat = Blueprint(
    name="chat",
    import_name=__name__,
    template_folder="templates"
)

# ストーリミング形式の応答を順番に格納するためのキューの準備
que = queue.Queue()
# デフォルトのsession_id
session_id = "defauly-session"
# Vector storeの読み込み
vectorstore = initialize_vectorstore()


# ルートエンドポイント
@chat.route('/')
def index():
    # ページがリロードされるたびにsession_idを更新する
    global session_id
    session_id = str(random.uniform(1, 100))
    logger.info("session_id:" + session_id)
    return render_template('chat/index.html')


# ボットアイコン表示用エンドポイント
@chat.route('/icon/boticon')
def icon():
    # アイコン画像の取得
    icon = os.path.dirname(__file__) + '/' + 'templates/chat/boticon.png'
    logger.info("icon:" + icon)
    # アイコンをWebサーバにダウンロード
    return send_file(icon, mimetype='image/png')


# 回答作成用エンドポイント
@chat.route('/ask')
def ask():

    history = CosmosDBChatMessageHistory(
        cosmos_endpoint=os.environ["COSMOS_ENDPOINT"],
        cosmos_database="langchain-chatbot",
        cosmos_container="history",
        credential=os.environ["COSMOS_CREDENTIAL"],
        session_id=session_id,
        user_id="user"
    )
    history.prepare_cosmos()

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
@chat.route('/listen')
def listen():
    def stream():
        while True:
            msg = que.get()
            if msg is None:
                break
            yield f'data: {msg}\n\n'
    response = Response(stream(), mimetype='text/event-stream')
    return response
