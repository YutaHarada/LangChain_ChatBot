FROM python:3.11-buster AS builder

# 各種パッケージをインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# マルチステージビルドを使う。
FROM python:3.11-slim-buster

ARG APP_DIR="/home"

# スクリプトのコピー
COPY ./settings.py ${APP_DIR}/settings.py
COPY ./apps/ ${APP_DIR}/apps/
WORKDIR ${APP_DIR}

COPY --from=builder  /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

EXPOSE 5000

ENTRYPOINT [ "gunicorn" ]
CMD [ "-k", "gevent", "--config", "settings.py" ]

