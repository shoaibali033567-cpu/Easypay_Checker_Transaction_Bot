# pages/api/inquire-easypay.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/api/inquire-easypay", methods=["GET"])
def inquire():
    order_id = request.args.get("order_id")
    if not order_id:
        return jsonify({"error": "missing order_id"}), 400

    try:
        # Make a request to your existing inquiry page
        res = requests.get(
            "https://naspropvt.vercel.app/inquire-easypay",
            params={"order_id": order_id},
            timeout=10
        )

        html = res.text.lower()

        # Detect transaction result by text on the page
        if "transaction successful" in html:
            return jsonify({"transactionStatus": "PAID", "settlementStatus": "SETTLED"})
        elif "transaction failed" in html:
            return jsonify({"transactionStatus": "FAILED", "settlementStatus": "UNSETTLED"})
        else:
            return jsonify({"transactionStatus": "UNKNOWN", "settlementStatus": "UNKNOWN"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
