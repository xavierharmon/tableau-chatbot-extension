import sys
import os

# Ensure src/ is on the path regardless of where app.py is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv

from groq_client     import GroqClient
from file_handler    import FileHandler
from tableau_bridge  import TableauBridge

load_dotenv()

app     = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-me")

# ── Per-process singletons ────────────────────────────────────────────────────
groq    = GroqClient()
files   = FileHandler()

# ── Simple in-memory session store (single-user local dev) ───────────────────
_bridge = TableauBridge()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    """Receive an Excel/CSV file, parse it, store context in session."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f        = request.files["file"]
    filename = f.filename or "upload"

    try:
        parsed = files.parse(f.read(), filename)
        _bridge.load_data(parsed)
        return jsonify({"ok": True, "summary": _bridge.summary()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Receive a user message, call Groq, return the assistant reply."""
    if not _bridge.data_ready:
        return jsonify({"error": "No data loaded yet"}), 400

    body    = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    _bridge.add_message("user", message)

    try:
        reply = groq.chat(_bridge.history, _bridge.data_context)
        _bridge.add_message("assistant", reply)
        return jsonify({"reply": reply})
    except Exception as e:
        # Roll back the user message on failure
        _bridge.history.pop()
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    """Clear loaded data and conversation history."""
    _bridge.reset()
    return jsonify({"ok": True})


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(_bridge.summary())


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=True)