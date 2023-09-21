import os
from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
import constants
from flask_cors import CORS

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)
app.debug = True
# app.secret_key = constants.SECRET_KEY

#app.config.from_object(config("APP_SETTINGS"))
bcrypt = Bcrypt(app)
mail = Mail(app)

#register blue print
from application.APIs.api import api_bp

app.register_blueprint(api_bp)
