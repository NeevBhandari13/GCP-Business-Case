import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db():
    # Cloud SQL Auth Proxy runs as a sidecar and listens on a Unix socket.
    # DB_HOST is the socket directory: /cloudsql/PROJECT:REGION:INSTANCE
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


@app.route("/health")
def health():
    # Liveness + readiness probe target. GKE will not route traffic to a pod
    # until this returns 200, and will restart the pod if it stops returning 200.
    return jsonify({"status": "ok"})


@app.route("/checkout", methods=["POST"])
def checkout():
    """Place an order for a card listing."""
    data = request.get_json(silent=True) or {}

    card_id = data.get("card_id")
    quantity = data.get("quantity", 1)
    buyer_email = data.get("buyer_email")

    if not card_id or not buyer_email:
        return jsonify({"error": "card_id and buyer_email are required"}), 400

    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO orders (card_id, quantity, buyer_email, status)
                    VALUES (%s, %s, %s, 'pending')
                    RETURNING id, created_at
                    """,
                    (card_id, quantity, buyer_email),
                )
                row = cur.fetchone()
        return jsonify({"order_id": row[0], "status": "pending", "created_at": row[1].isoformat()}), 201
    finally:
        conn.close()


@app.route("/orders", methods=["GET"])
def orders():
    """Return the 20 most recent orders."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, card_id, quantity, buyer_email, status, created_at FROM orders ORDER BY created_at DESC LIMIT 20"
            )
            rows = cur.fetchall()
        return jsonify([dict(r) | {"created_at": r["created_at"].isoformat()} for r in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
