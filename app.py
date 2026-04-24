from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return "Linux Monitor API "


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

DB = "database.db"


def query_db(query):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


@app.route("/metrics")
def metrics():
    rows = query_db("""
        SELECT timestamp, cpu, memory, disk
        FROM metrics
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    data = [
        {
            "timestamp": r[0],
            "cpu": r[1],
            "memory": r[2],
            "disk": r[3],
        }
        for r in rows
    ]

    return jsonify(data)


@app.route("/alerts")
def alerts():
    rows = query_db("""
        SELECT timestamp, message, cpu, memory, disk
        FROM alerts
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    data = [
        {
            "timestamp": r[0],
            "message": r[1],
            "cpu": r[2],
            "memory": r[3],
            "disk": r[4],
        }
        for r in rows
    ]

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
