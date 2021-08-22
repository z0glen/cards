from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
import sys


app = Flask(__name__)

app.logger = logging.getLogger(__name__)
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

CORS(app)
socketIO = SocketIO(app, cors_allowed_origins="*")

app.secret_key = os.environ.get('SECRET_KEY', 'dev')
app.password = os.environ.get('CARDS_PASSWORD', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
