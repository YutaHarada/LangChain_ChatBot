# import文
from langchain.callbacks.base import BaseCallbackHandler


class MyCustomCallbackHandler(BaseCallbackHandler):

    def __init__(self, que):
        self.que = que

    # LLMからの応答ストリームによって文言を受け取るたびに呼び出されるメソッド
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.que.put(token)
