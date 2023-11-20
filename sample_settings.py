import os

# Gunicorn config file
wsgi_app = 'apps.app:create_app("staging")'
# wsgi_app = 'apps.app:create_app("develop")'

# Server Mechanics
# ========================================
# current directory
chdir = os.path.dirname(__file__)

# daemon mode
daemon = False

# enviroment variables
raw_env = [
    'OPENAI_API_KEY=...',
    'OPENAI_API_MODEL=...',
    'OPENAI_API_TEMPERATURE=...',
    'PINECONE_API_KEY=...',
    'PINECONE_INDEX=...',
    'PINECONE_ENV=...'
]

# Server Socket
# ========================================
bind = '127.0.0.1:5000'

# Worker Processes
# ========================================
workers = 1

#  Logging
# ========================================
# access log
# accesslog = os.path.dirname(__file__) + '/' + 'logs/access.log'
accesslog = '-'

# gunicorn log
errorlog = '-'
loglevel = 'info'
# loglevel = 'debug'
