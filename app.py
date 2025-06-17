from flask import Flask, jsonify
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Config
USERNAME = "d5900938-be95-4412-95b3-50b11983e13e"
PASSWORD = "90fa0de5-250a-4e99-bd65-85b1854d9c82"
BASE_URL = "http://102.33.60.228:9183/getResources"

@app.route('/')
def home():
    return jsonify({"message": "✅ Flask API is running. Visit /api/sales-live for live sales data."})


@app.route('/api/sales-live', methods=['GET'])
def live_sales_by_rep():
    endpoint = f"{BASE_URL}/customer_transactions?max=1000"

    try:
        response = requests.get(
            endpoint,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers={"Accept": "application/json"},
            timeout=30
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Failed to fetch data",
                "status_code": response.status_code,
                "details": response.text
            }), response.status_code

        transactions = response.json().get("customer_transactions", [])
        sales_today = defaultdict(float)

        today = datetime.today().date()

        for tx in transactions:
            tx_date_raw = tx.get("transaction_date", "")
            try:
                tx_date = datetime.strptime(tx_date_raw, "%m-%d-%Y").date()
                if tx_date == today:
                    rep_code = tx.get("sales_rep_code")
                    amount = float(tx.get("amount", 0))
                    if rep_code:
                        sales_today[rep_code] += amount
            except ValueError:
                continue  # skip invalid date formats

        result = {
            "date": today.isoformat(),
            "sales_data": [
                {"sales_rep_code": rep, "total_sales": round(sales, 2)}
                for rep, sales in sorted(sales_today.items(), key=lambda x: -x[1])
            ]
        }

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Request failed", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
