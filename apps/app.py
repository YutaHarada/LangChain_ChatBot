# import文
import logging

from flask import Flask

from apps.modules.debugger import inner_log

# ロガーの初期化
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def create_app(config_key):

    # Flaskアプリの初期化
    app = Flask(__name__)

    # 内部処理確認の有無
    inner_log(config_key)

    from apps.chat import views as chat_views

    app.register_blueprint(blueprint=chat_views.chat, url_prefix="/")

    return app
