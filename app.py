#! /usr/bin/env python3.5
from flask import Flask
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "cateringpos"
app.settings = {}
app.program_name="CateringPOS"
