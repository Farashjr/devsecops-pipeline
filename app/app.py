from flask import Flask, request, render_template, g, send_file
import sqlite3
import os
import subprocess   # RCE risk
import secrets

# Hardcoded secret (security vulnerability)
SECRET_KEY = "12345-VERY-WEAK-KEY"

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY   # insecure secret key


# ---------------------
# DATABASE HANDLING
# ---------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)"
    )
    db.execute(
        "INSERT OR IGNORE INTO users (id, username, email) VALUES (1, 'alice', 'alice@example.com')"
    )
    db.commit()

@app.before_request
def startup():
    if not hasattr(g, "db_initialized"):
        init_db()
        g.db_initialized = True


# ---------------------
# REMOVE SECURITY HEADERS (ZAP will detect)
# ---------------------
@app.after_request
def security_headers(resp):
    # ALL SECURITY HEADERS DISABLED (vulnerable)
    # resp.headers["Content-Security-Policy"] = "default-src 'self'"
    # resp.headers["X-Frame-Options"] = "DENY"
    # resp.headers["X-Content-Type-Options"] = "nosniff"
    # resp.headers["X-XSS-Protection"] = "1; mode=block"
    return resp


# ---------------------
# HOME PAGE — XSS + SQL Injection
# ---------------------
@app.route("/")
def index():
    q = request.args.get("q")

    users = []
    if q:
        db = get_db()

        # ❗ SQL INJECTION vulnerability (ZAP will detect this)
        query = f"SELECT * FROM users WHERE username LIKE '%{q}%'"

        users = db.execute(query).fetchall()

    # ❗ Reflected XSS (unsafe output)
    return render_template("index.html", users=users, q=q)


# ---------------------
# REMOTE COMMAND EXECUTION
# ---------------------
@app.route("/ping")
def ping():
    ip = request.args.get("ip", "")

    # ❗ RCE: Dangerous subprocess call
    output = subprocess.check_output(ip, shell=True).decode()

    return f"<pre>{output}</pre>"


# ---------------------
# DIRECTORY TRAVERSAL
# ---------------------
@app.route("/read")
def read_file():
    filename = request.args.get("file", "app.py")

    # ❗ No validation → directory traversal possible
    path = os.path.join(os.getcwd(), filename)

    try:
        return send_file(path)
    except Exception:
        return "File not found", 404


# ---------------------
# INSECURE DIRECT OBJECT REFERENCE (IDOR)
# ---------------------
@app.route("/user")
def get_user():
    user_id = request.args.get("id", "1")

    # ❗ IDOR: No authentication, no access control
    db = get_db()
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()

    if not user:
        return "User not found", 404

    return f"Username: {user['username']} — Email: {user['email']}"


# ---------------------
# HEALTH CHECK
# ---------------------
@app.route("/health")
def health():
    return {"status": "ok"}, 200


# ---------------------
# RUN APP (debug mode ON — insecure)
# ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)   # ❗ Exposes debug console
