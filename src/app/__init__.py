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

# WSGI middleware that sets SCRIPT_NAME from a forwarded header to serve the app under a subpath when behind a reverse proxy
# -> SCRIPT_NAME = the mount point or subpath under which the app is accessible (e.g., /agent-directory).
# -> PATH_INFO = the remaining part of the URL that the app routes (e.g., /static/css/app.css).
class PrefixMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Determine Subpath of the application from HTTP headers or environment variable
        # -> Prefer X-Script-Name, fallback to X-Forwarded-Prefix as HTTP header set by proxy, alternatively fallback to APP_SUBPATH env var
        script_name = environ.get('HTTP_X_SCRIPT_NAME') or environ.get('HTTP_X_FORWARDED_PREFIX')
        if not script_name:
            # APP_SUBPATH may be set as an environment variable without leading slash
            app_subpath = os.getenv('APP_SUBPATH', '')
            if app_subpath:
                script_name = '/' + app_subpath.strip('/')
        
        # Use SCRIPT_NAME and PATH_INFO to correctly route to application resources when behind a reverse proxy with a subpath
        if script_name:
            # First, ensure SCRIPT_NAME starts with '/'
            print(f"PrefixMiddleware: Setting SCRIPT_NAME to '{script_name}' from HTTP header or environment variable")
            if not script_name.startswith('/'):
                script_name = '/' + script_name
            # strip trailing slash
            if script_name != '/' and script_name.endswith('/'):
                script_name = script_name.rstrip('/')

            # Second, set SCRIPT_NAME in the WSGI environment and adjust PATH_INFO accordingly
            environ['SCRIPT_NAME'] = script_name
            path_info = environ.get('PATH_INFO', '')
            # If PATH_INFO begins with the script_name, remove that part so Flask routing works
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):] or '/'

        return self.app(environ, start_response)

# get environment variable for subpath (used as fallback for URL generation)
APP_SUBPATH = os.getenv("APP_SUBPATH", "").strip('/')
if APP_SUBPATH:
    script_root = '/' + APP_SUBPATH
    print(f"Starting app with subpath: {script_root}")
    application_root = script_root
else:
    print("Starting app without subpath, using root path")
    application_root = ''

# Use a fixed static_url_path; URL generation will include SCRIPT_NAME via middleware
static_path = '/static'

app = Flask(__name__, static_url_path=static_path)
app.config["APPLICATION_ROOT"] = application_root or '/'
app.config["APP_SUBPATH"] = APP_SUBPATH
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

# Wrap WSGI app with PrefixMiddleware so SCRIPT_NAME is set from X-Script-Name/X-Forwarded-Prefix
app.wsgi_app = PrefixMiddleware(app.wsgi_app)
