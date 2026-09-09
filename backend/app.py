from flask import Flask, jsonify, request
import os
import socket
import time

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "phase1-mini-app")
DB_HOST = os.getenv("DB_HOST", "192.168.56.11")
DB_NAME = os.getenv("DB_NAME", "appdb")
STARTED_AT = time.time()


@app.after_request
def add_cors_headers(response):
    # Erlaube Browser-Direktzugriffe auf die API (lokale Entwicklung ohne
    # Reverse Proxy). Hinter dem Frontend-Nginx unnoetig, aber unschaedlich.
    response.headers["Access-Control-Allow-Origin"] = os.getenv("CORS_ORIGIN", "*")
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def get_db_connection():
    """Stelle eine DB-Verbindung her. Liefere None bei Fehlschlag."""
    import psycopg2

    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=os.getenv("DB_USER", "app"),
        password=os.getenv("DB_PASSWORD", "changeme"),
        connect_timeout=3,
    )


def ensure_notes_table():
    """Lege die notes-Tabelle an, falls sie fehlt."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            text VARCHAR(500) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.get("/")
def index():
    return jsonify(
        service=APP_NAME,
        host=socket.gethostname(),
        message="Phase I mini-challenge API - nutze das Frontend auf der frontend-VM",
        endpoints=["/health", "/api/hello", "/api/info", "/api/db", "/api/notes"],
    )


@app.get("/health")
def health():
    # bewusst simpel: Liveness ohne DB-Abhängigkeit (stateless API)
    return jsonify(status="ok", service=APP_NAME), 200


@app.get("/api/info")
def info():
    return jsonify(
        service=APP_NAME,
        host=socket.gethostname(),
        uptime_seconds=int(time.time() - STARTED_AT),
        db_host=DB_HOST,
        db_name=DB_NAME,
        endpoints=["/health", "/api/hello", "/api/info", "/api/db", "/api/notes"],
    )


@app.get("/api/hello")
def hello():
    return jsonify(msg="hello from api", db_host=DB_HOST, db_name=DB_NAME)


@app.get("/api/db")
def db_check():
    """Pruefe die DB-Verbindung. Liefere 200 bei Erfolg, sonst 503.

    Lies DB_HOST/DB_USER/DB_PASSWORD aus der Umgebung (per Secret-Management
    und Compose-Env setzen). Verwende kein ORM - weise nur nach,
    dass app -> db geht.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify(status="ok", db_version=version), 200
    except Exception as exc:  # noqa: BLE001 - bewusst generisch für Lehrzweck
        return jsonify(status="error", detail=str(exc)[:300]), 503


@app.get("/api/notes")
def list_notes():
    """Liefere die neuesten Notizen. Liefere 503 bei unerreichbarer DB."""
    try:
        ensure_notes_table()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 50;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(
            notes=[
                {"id": r[0], "text": r[1], "created_at": str(r[2])} for r in rows
            ]
        ), 200
    except Exception as exc:  # noqa: BLE001 - bewusst generisch für Lehrzweck
        return jsonify(status="error", detail=str(exc)[:300]), 503


@app.post("/api/notes")
def create_note():
    """Lege eine Notiz an. Erwarte JSON {"text": "..."}. Liefere 201/400/503."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(status="error", detail="Feld 'text' fehlt oder ist leer."), 400
    if len(text) > 500:
        return jsonify(status="error", detail="Feld 'text' ist zu lang (max. 500)."), 400
    try:
        ensure_notes_table()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id;", (text,)
        )
        note_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(id=note_id, text=text), 201
    except Exception as exc:  # noqa: BLE001 - bewusst generisch für Lehrzweck
        return jsonify(status="error", detail=str(exc)[:300]), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
