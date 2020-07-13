from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
app.config.from_object('src.config')
CORS(app)

from src.api import auth, select