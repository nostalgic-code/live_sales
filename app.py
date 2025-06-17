from flask import Flask, jsonify, render_template
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Configuration
USERNAME = "d5900938-be95-4412-95b3-50b11983e13e"
PASSWORD = "90fa0de5-250a-4e99-bd65-85b1854d9c82"
BASE_URL = "http://102.33.60.228:9183/getResources"

@app.route('/')
def dashboard():
    return render_template("index.html")

@app.route('/api/sales-live', methods=['GET'])
def live_sales_by_rep():
    url = f"{BASE_URL}/customer_transactions?max=1000"

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers={"Accept": "application/json"},
            timeout=30
        )
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data", "status": response.status_code}), response.status_code

        transactions = response.json().get("customer_transactions", [])
        sales_today = defaultdict(float)

        today = datetime.today().date()

        for tx in transactions:
            try:
                tx_date = datetime.strptime(tx.get("transaction_date", ""), "%m-%d-%Y").date()
                if tx_date == today and tx.get("sales_rep_code") and tx.get("amount"):
                    rep = tx["sales_rep_code"]
                    amount = float(tx["amount"])
                    sales_today[rep] += amount
            except Exception:
                continue

        return jsonify({
            "date": today.isoformat(),
            "sales_data": [{"sales_rep_code": rep, "total_sales": round(amount, 2)} for rep, amount in sales_today.items()]
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
