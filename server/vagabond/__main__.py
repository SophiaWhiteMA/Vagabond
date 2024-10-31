'''
    In an effort to be more Pythonic, Vagabond does not use
    Flask blueprints and instead uses standard python imports/exports
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path='/')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_SERVER']}:{os.environ['MYSQL_PORT']}/{os.environ['MYSQL_DATABASE']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'v5t8IIbv7c8xw59sqoQInUHEouXqVLSHrvw0Ggk00_BiBNSBXH--qU_tiwGER8uf_-vsOdh6Pjwf2vYL1I_U7-rdFYvZ-C2C6sYokT6HGww-WaH97BGrRKHcUmt0kFb-sJRfAFik5-QPERSXEdmCya4uvRRVxX8bI2126dbM20A'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)
limiter = Limiter(app)
cors = CORS(app)

from vagabond.models import *
from vagabond.routes import *


db.create_all()

if __name__ == '__main__':
    app.run()
