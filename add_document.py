# import文
import logging
import os
import sys

import pinecone
from dotenv import load_dotenv
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone

# 環境変数の読み込み
load_dotenv()

# ロガーの初期化
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Vector storeの準備
def initialize_vectorstore():
    # pineconeの初期化
    pinecone.init(
        api_key=os.environ["PINECONE_API_KEY"],
        environment=os.environ["PINECONE_ENV"]
    )

    # index名の設定
    index_name = os.environ["PINECONE_INDEX"]
    # 埋め込み処理の初期化
    embeddings = OpenAIEmbeddings()
    return Pinecone.from_existing_index(index_name, embeddings)


# 文書をPineconeに保存する
if __name__ == "__main__":
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
    vectorstore.add_documents(docs)
