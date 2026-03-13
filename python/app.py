import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from groq_client      import GroqClient
from file_handler     import FileHandler
from tableau_bridge   import TableauBridge
from context_manager  import ContextManager

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-me")

# Singletons
groq    = GroqClient()
files   = FileHandler()
_bridge = TableauBridge()
context = ContextManager()

# Load role config — try Excel file first, fall back to defaults
CONFIG_PATH = os.path.join(BASE_DIR, "context_config.xlsx")
if os.path.exists(CONFIG_PATH):
    context.load_from_excel(CONFIG_PATH)
else:
    context.load_defaults()


@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/api/roles", methods=["GET"])
def get_roles():
    return jsonify({
        "roles":       context.get_roles_list(),
        "active_role": context.active_role
    })


@app.route("/api/roles/set", methods=["POST"])
def set_role():
    body    = request.get_json(silent=True) or {}
    role_id = (body.get("role_id") or "").strip().lower()
    if not role_id:
        return jsonify({"error": "role_id is required"}), 400
    context.set_role(role_id)
    return jsonify({"ok": True, "active_role": context.active_role, "role": context.get_role()})


@app.route("/api/upload", methods=["POST"])
def upload():
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
    if not _bridge.data_ready:
        return jsonify({"error": "No data loaded yet"}), 400
    body    = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400
    _bridge.add_message("user", message)
    role_context = context.build_role_context()
    try:
        reply = groq.chat(_bridge.history, _bridge.data_context, role_context)
        _bridge.add_message("assistant", reply)
        return jsonify({"reply": reply, "active_role": context.active_role})
    except Exception as e:
        _bridge.history.pop()
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    _bridge.reset()
    return jsonify({"ok": True})


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({**_bridge.summary(), "active_role": context.active_role})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=True)