import os
from flask import Flask, Blueprint
import config

app = Flask(__name__)
app.config.from_object(config.Configuration)

# Blueprints
from api.app import api

@app.route('/')
def root():
    out = "RPI nfc + label tagger"
    return out

app.register_blueprint(api)

if __name__ == '__main__':
    app.run(host = '0.0.0.0')