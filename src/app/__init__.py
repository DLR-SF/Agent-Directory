import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__, static_url_path='/static')
CORS(app, origins="*")
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#login = LoginManager(app)
#login.login_view = 'login'

# local bootstrap
bootstrap = Bootstrap(app)
# serve bootstrap locally
# app.config['BOOTSTRAP_SERVE_LOCAL'] = True

if not app.debug:
    # create log
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/agent-directory.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('agent-directory startup')

from app import routes, models, errors, platformHandler, configurationHandler
