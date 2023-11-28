# import文
import sys
import os
import logging
from dotenv import load_dotenv

from langchain.document_loaders import UnstructuredPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.azuresearch import AzureSearch


# 環境変数の読み込み
load_dotenv()


# Vector storeの準備
def initialize_vectorstore():
    # AzureSearchの接続情報の取得
    azure_search_endpoint = os.environ["VECTOR_STORE_ADDRESS"]
    azure_search_key = os.environ["VECTOR_STORE_PASSWORD"]
    # index名の取得
    index_name = os.environ["INDEX_NAME"]

    # 埋め込み処理の初期化
    embeddings = OpenAIEmbeddings()

    # CosmosDBの初期化
    vectorstore = AzureSearch(
        azure_search_endpoint=azure_search_endpoint,
        azure_search_key=azure_search_key,
        index_name=index_name,
        embedding_function=embeddings.embed_query,
    )

    return vectorstore


# 文書をPineconeに保存する
if __name__ == "__main__":
    # ロガーの初期化
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    # 読み込むドキュメントのパスを取得
    file_path = sys.argv[1]
    # PDFファイルの読み込み
    loader = UnstructuredPDFLoader(file_path)
    raw_docs = loader.load()
    logger.info("Loaded %d documents", len(raw_docs))

    # 読み込んだ文書をチャンクに分割
    test_spliter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    docs = test_spliter.split_documents(raw_docs)
    logger.info("Split %d documents", len(docs))

    # Vector storeの初期化
    vectorstore = initialize_vectorstore()
    # ベクトル化した文書の追加
    vectorstore.add_documents(documents=docs)
