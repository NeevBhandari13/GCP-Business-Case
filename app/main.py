import os
from flask import Flask, jsonify, request
from google.cloud.sql.connector import Connector

app = Flask(__name__)

# The connector uses Application Default Credentials automatically.
# On GKE with Workload Identity, that resolves to the pod's Google service account —
# no static keys or passwords required.
connector = Connector()


def get_db():
    conn = connector.connect(
        os.environ["INSTANCE_CONNECTION_NAME"],  # PROJECT:REGION:INSTANCE
        "pymysql",
        user=os.environ["DB_USER"],              # the bound service account email
        db=os.environ["DB_NAME"],
        enable_iam_auth=True,
    )
    conn.autocommit = True
    return conn


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json(silent=True) or {}
    card_id = data.get("card_id")
    buyer_email = data.get("buyer_email")

    if not card_id or not buyer_email:
        return jsonify({"error": "card_id and buyer_email are required"}), 400

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO orders (card_id, quantity, buyer_email) VALUES (%s, %s, %s)",
            (card_id, data.get("quantity", 1), buyer_email),
        )
        order_id = cur.lastrowid
    conn.close()

    return jsonify({"order_id": order_id, "status": "pending"}), 201


@app.route("/orders", methods=["GET"])
def orders():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, card_id, quantity, buyer_email, status, created_at FROM orders ORDER BY created_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
    conn.close()

    keys = ["id", "card_id", "quantity", "buyer_email", "status", "created_at"]
    return jsonify([dict(zip(keys, r)) | {"created_at": str(r[5])} for r in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
