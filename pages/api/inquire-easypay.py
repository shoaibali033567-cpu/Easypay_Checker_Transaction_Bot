# api/inquire-easypay.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/inquire-easypay", methods=["GET"])
def inquire():
    order_id = request.args.get("order_id")
    if not order_id:
        return jsonify({"error": "missing order_id"}), 400

    # placeholder response for now (we'll replace this with real logic next step)
    return jsonify({"transactionStatus": "UNKNOWN", "settlementStatus": "UNKNOWN"})
