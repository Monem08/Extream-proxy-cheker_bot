from flask import Flask, jsonify

app = Flask(__name__)


# 🏠 ROOT (CRON USE THIS)
@app.route("/")
def home():
    return jsonify({
        "status": "Bot is alive",
        "service": "Proxy Checker Bot",
        "uptime": "running"
    })


# ❤️ HEALTH CHECK (OPTIONAL)
@app.route("/health")
def health():
    return "OK", 200


# 🔥 PING ROUTE (EXTRA SAFE)
@app.route("/ping")
def ping():
    return "pong", 200
