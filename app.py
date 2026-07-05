from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('focus.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS distractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            time TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT,
            end TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- FRONTEND ----------------
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ---------------- START SESSION ----------------
@app.route('/start', methods=['POST'])
def start():
    conn = sqlite3.connect('focus.db')
    c = conn.cursor()

    # prevent multiple sessions
    c.execute("SELECT * FROM sessions WHERE end IS NULL")
    active = c.fetchone()

    if active:
        conn.close()
        return jsonify({"message": "already running"})

    c.execute("INSERT INTO sessions (start, end) VALUES (?, ?)",
              (datetime.now(), None))

    conn.commit()
    conn.close()
    return jsonify({"message": "started"})

# ---------------- STOP SESSION ----------------
@app.route('/stop', methods=['POST'])
def stop():
    conn = sqlite3.connect('focus.db')
    c = conn.cursor()

    # update only latest active session
    c.execute("SELECT id FROM sessions WHERE end IS NULL ORDER BY id DESC LIMIT 1")
    row = c.fetchone()

    if row:
        c.execute("UPDATE sessions SET end=? WHERE id=?",
                  (datetime.now(), row[0]))
        conn.commit()

    conn.close()
    return jsonify({"message": "stopped"})

# ---------------- ADD DISTRACTION ----------------
@app.route('/add_distraction', methods=['POST'])
def add_distraction():
    data = request.json

    conn = sqlite3.connect('focus.db')
    c = conn.cursor()

    c.execute("INSERT INTO distractions (name, time) VALUES (?, ?)",
              (data['name'], datetime.now()))

    conn.commit()
    conn.close()
    return jsonify({"message": "added"})

# ---------------- GET DATA ----------------
@app.route('/data')
def get_data():
    conn = sqlite3.connect('focus.db')
    c = conn.cursor()

    c.execute("SELECT * FROM distractions ORDER BY id DESC")
    distractions = c.fetchall()

    c.execute("SELECT * FROM sessions ORDER BY id DESC")
    sessions = c.fetchall()

    conn.close()

    return jsonify({
        "distractions": distractions,
        "sessions": sessions
    })

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)