# import文
import langchain


def inner_log(env: str):
    if env == "develop":
        # LangChainの内部処理を確認するための設定
        langchain.verbose = True
        langchain.debug = True
