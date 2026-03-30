from flask import Flask, jsonify
import logging

app = Flask(__name__)

# 💀 disable logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/")
def home():
    return jsonify({
        "status": "Bot is Online!"
    })
