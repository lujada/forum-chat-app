# venv command = venv\Scripts\activate
# flask run

from flask import Flask
from os import getenv
import sys
import logging
import secrets

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

import routes