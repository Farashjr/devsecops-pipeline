from flask import Flask, request, render_template, g
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

app = Flask(__name__)

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

@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-XSS-Protection"] = "1; mode=block"
    return resp

@app.route("/")
def index():
    q = request.args.get("q")
    users = []
    if q:
        # SAFE parameterized query
        db = get_db()
        users = db.execute(
            "SELECT * FROM users WHERE username LIKE ?", (f"%{q}%",)
        ).fetchall()
    return render_template("index.html", users=users, q=q or "")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
