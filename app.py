import json
from flask import Flask, jsonify, request
from mysql.connector import Error, IntegrityError
from db import get_connection, fetch_all
from analysis import build_rfm, rule_segments, kmeans_segments, summary, make_charts

app = Flask(__name__)

def fail(message, status=400):
    return jsonify({"error": message}), status

def load_data():
    return (
        fetch_all("SELECT customer_id, customer_code, signup_date FROM customers"),
        fetch_all("SELECT order_id, customer_id, order_date, order_status FROM orders"),
        fetch_all("SELECT item_id, order_id, quantity, unit_price FROM order_items")
    )

@app.get("/")
def home():
    return jsonify({"project": "Customer Segmentation and Predictive Analytics System",
                    "status": "running",
                    "routes": ["/health", "/api/customers", "/api/orders",
                               "/api/analysis/rfm", "/api/analysis/segments",
                               "/api/analysis/summary"]})

@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Error:
        return fail("Database connection failed. Check .env and confirm MySQL is running.", 503)

@app.get("/api/customers")
def customers_list():
    try:
        return jsonify(fetch_all("SELECT customer_id, customer_code, signup_date FROM customers ORDER BY customer_id"))
    except Error:
        return fail("Could not read customers from MySQL.", 503)

@app.post("/api/customers")
def customer_create():
    data = request.get_json(silent=True) or {}
    code = str(data.get("customer_code", "")).strip()
    signup_date = data.get("signup_date") or None
    if not code:
        return fail("customer_code is required.")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (customer_code, signup_date) VALUES (%s, %s)", (code, signup_date))
        conn.commit()
        return jsonify({"customer_id": cursor.lastrowid, "customer_code": code}), 201
    except IntegrityError:
        conn.rollback()
        return fail("That customer_code already exists.", 409)
    except Error:
        conn.rollback()
        return fail("Could not save customer. Check the date format and database.", 400)
    finally:
        cursor.close()
        conn.close()

@app.get("/api/orders")
def orders_list():
    try:
        rows = fetch_all("""
          SELECT o.order_id, o.customer_id, c.customer_code, o.order_date, o.order_status,
                 COALESCE(SUM(i.quantity*i.unit_price),0) AS order_total
          FROM orders o JOIN customers c ON c.customer_id=o.customer_id
          LEFT JOIN order_items i ON i.order_id=o.order_id
          GROUP BY o.order_id, o.customer_id, c.customer_code, o.order_date, o.order_status
          ORDER BY o.order_date DESC
        """)
        for row in rows:
            row["order_total"] = float(row["order_total"])
        return jsonify(rows)
    except Error:
        return fail("Could not read orders from MySQL.", 503)

@app.post("/api/orders")
def order_create():
    data = request.get_json(silent=True) or {}
    try:
        customer_id = int(data.get("customer_id"))
        quantity = int(data.get("quantity"))
        price = float(data.get("unit_price"))
    except (TypeError, ValueError):
        return fail("customer_id, quantity and unit_price must be valid numbers.")
    order_date = data.get("order_date")
    status = str(data.get("order_status", "completed")).lower()
    if not order_date: return fail("order_date is required as YYYY-MM-DD.")
    if quantity <= 0 or price < 0: return fail("quantity must be positive and unit_price cannot be negative.")
    if status not in {"completed", "pending", "cancelled"}:
        return fail("order_status must be completed, pending or cancelled.")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO orders (customer_id, order_date, order_status) VALUES (%s,%s,%s)",
                       (customer_id, order_date, status))
        order_id = cursor.lastrowid
        cursor.execute("INSERT INTO order_items (order_id, quantity, unit_price) VALUES (%s,%s,%s)",
                       (order_id, quantity, price))
        conn.commit()
        return jsonify({"order_id": order_id, "order_total": round(quantity*price, 2)}), 201
    except Error:
        conn.rollback()
        return fail("Could not save order. Confirm customer_id exists and the date is valid.", 400)
    finally:
        cursor.close()
        conn.close()

@app.get("/api/analysis/rfm")
def rfm_report():
    try:
        c, o, i = load_data()
        r = rule_segments(build_rfm(c, o, i))
        records = r.to_dict(orient="records")
        for row in records: row["monetary"] = round(float(row["monetary"]), 2)
        return jsonify({"count": len(records), "rfm": records})
    except Error:
        return fail("Could not load data for RFM analysis.", 503)

@app.post("/api/analysis/segments")
def segment_run():
    data = request.get_json(silent=True) or {}
    method = str(data.get("method", "rules")).lower()
    try:
        c, o, i = load_data()
        r = build_rfm(c, o, i)
        if r.empty: return fail("Add customers before running segmentation.")
        if method == "rules":
            out, params = rule_segments(r), {"rules_version": 1}
        elif method == "kmeans":
            n = int(data.get("n_clusters", 3))
            out, params = kmeans_segments(r, n), {"n_clusters": n}
        else:
            return fail("method must be 'rules' or 'kmeans'.")
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO segment_runs (method, parameters_json) VALUES (%s,%s)",
                           (method, json.dumps(params)))
            run_id = cursor.lastrowid
            values = [(run_id, int(x.customer_id), str(x.segment_label), int(x.recency_days),
                       int(x.frequency), float(x.monetary)) for x in out.itertuples()]
            cursor.executemany("""INSERT INTO customer_segments
                (run_id, customer_id, segment_label, recency_days, frequency, monetary)
                VALUES (%s,%s,%s,%s,%s,%s)""", values)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close(); conn.close()
        charts = make_charts(out)
        return jsonify({"run_id": run_id, "method": method, "customers_segmented": len(out),
                        "summary": summary(out), "charts": charts}), 201
    except ValueError as exc:
        return fail(str(exc))
    except Error:
        return fail("Database error while saving segmentation. Check schema.sql and .env.", 503)

@app.get("/api/analysis/summary")
def saved_summary():
    try:
        run = fetch_all("SELECT run_id, method, run_date FROM segment_runs ORDER BY run_id DESC LIMIT 1")
        if not run:
            return jsonify({"message": "No segmentation run yet. POST to /api/analysis/segments first."})
        rows = fetch_all("""SELECT segment_label, COUNT(*) AS customer_count,
            ROUND(AVG(recency_days),2) AS average_recency_days,
            ROUND(AVG(frequency),2) AS average_frequency,
            ROUND(AVG(monetary),2) AS average_monetary,
            ROUND(SUM(monetary),2) AS total_monetary
            FROM customer_segments WHERE run_id=%s GROUP BY segment_label ORDER BY customer_count DESC""",
            (run[0]["run_id"],))
        for row in rows:
            row["average_monetary"] = float(row["average_monetary"])
            row["total_monetary"] = float(row["total_monetary"])
        return jsonify({"run": run[0], "summary": rows})
    except Error:
        return fail("Could not read saved summary.", 503)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    app.run(host=os.getenv("FLASK_HOST", "127.0.0.1"),
            port=int(os.getenv("FLASK_PORT", "5000")), debug=True)
