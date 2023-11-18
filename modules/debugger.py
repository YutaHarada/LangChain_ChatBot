# import文
import langchain


def inner_log(debug: bool):
    if debug:
        # LangChainの内部処理を確認するための設定
        langchain.verbose = True
        langchain.debug = True
