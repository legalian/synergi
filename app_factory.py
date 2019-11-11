from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.github import make_github_blueprint
from flask_session import Session
import os
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)
socketio = SocketIO(app)
# heroku = Heroku(app)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Session(app)

blueprint = make_github_blueprint(
    client_id=os.environ['GITHUB_CLIENT_ID'],
    client_secret=os.environ['GITHUB_CLIENT_SECRET'],
    scope = "repo"
)
app.register_blueprint(blueprint, url_prefix="/login")

migrate = Migrate(app, db)

