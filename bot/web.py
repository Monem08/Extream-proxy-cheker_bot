from flask import Flask, jsonify
import time
import os

app = Flask(__name__)

# ⏱ start time (uptime calculate)
START_TIME = time.time()


# 🏠 ROOT (CRON USE THIS)
@app.route("/")
def home():
    uptime = int(time.time() - START_TIME)

    return jsonify({
        "status": "Bot is alive",
        "service": "Proxy Checker Bot",
        "uptime_seconds": uptime
    })


# ❤️ HEALTH CHECK (FAST RESPONSE)
@app.route("/health")
def health():
    return "OK", 200


# 🔥 PING (ULTRA LIGHT)
@app.route("/ping")
def ping():
    return "pong", 200


# 📊 STATUS (ADVANCED DEBUG)
@app.route("/status")
def status():
    uptime = int(time.time() - START_TIME)

    return jsonify({
        "status": "running",
        "uptime": uptime,
        "environment": os.getenv("RENDER", "local"),
        "port": os.getenv("PORT", "10000")
    })


# ❌ 404 HANDLER (CLEAN)
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not Found",
        "message": "Invalid endpoint"
    }), 404


# 🚀 RUN (ONLY IF RUN DIRECTLY)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    print(f"🌐 Web server running on port {port}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False  # 💀 IMPORTANT
    )
