# Customer Segmentation and Predictive Analytics System

A student project using Python, Flask, MySQL, Pandas, NumPy, Matplotlib, and optional scikit-learn K-means clustering.

## Setup in VS Code (Windows)
1. Extract the ZIP and open this folder in VS Code.
2. Open Terminal → New Terminal.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, choose Command Prompt terminal and run `.venv\Scripts\activate.bat`.
4. Install dependencies: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`.
5. Copy `.env.example` to `.env`; add your MySQL password. Do not share `.env`.
6. In MySQL Workbench, run `schema.sql`, then run `seed.sql` once on the fresh database.
7. Start the server with `python app.py`.
8. Visit `http://127.0.0.1:5000/health`; expected response: `{"database":"connected","status":"ok"}`.

## API endpoints
- `GET /health` — database health check
- `GET /api/customers` — list customers
- `POST /api/customers` — add customer
- `GET /api/orders` — list orders
- `POST /api/orders` — add an order and one item
- `GET /api/analysis/rfm` — calculate RFM values and rule-based labels
- `POST /api/analysis/segments` — save a segmentation run
- `GET /api/analysis/summary` — summary for the latest saved run

### Add customer (POST `/api/customers`)
```json
{"customer_code":"CUST013","signup_date":"2026-10-01"}
```

### Add order (POST `/api/orders`)
Use a real `customer_id` from the customer endpoint:
```json
{"customer_id":1,"order_date":"2026-10-20","order_status":"completed","quantity":2,"unit_price":450}
```

### Run rule-based segmentation
POST `/api/analysis/segments` with JSON:
```json
{"method":"rules"}
```

### Run K-means (optional)
POST `/api/analysis/segments` with JSON:
```json
{"method":"kmeans","n_clusters":3}
```
The cluster count must be at least 2 and less than the number of customers.

After segmentation, inspect the three PNG charts created in the `charts` folder:
- `segment_distribution.png`
- `average_spend_by_segment.png`
- `average_frequency_by_segment.png`

## RFM definitions
- Recency: days between the most recent completed order and a reference date (one day after the latest order in the sample dataset).
- Frequency: number of distinct completed orders.
- Monetary: sum of quantity × unit price across completed order items.
- High-Value Active: recency <= 30, frequency >= 4, monetary >= 1000.
- Loyal Customer: recency <= 60 and frequency >= 3.
- At-Risk / Inactive: recency > 90.
- New / One-Time: exactly one completed order.
- Regular Customer: other customers with at least one completed order.
- No Purchase Yet: no completed orders.

The rules are illustrative and should be explained as chosen thresholds, not universal truths. Data is synthetic. The API-focused version has no separate frontend, which is allowed by the project brief.

## Suggested tests
1. Valid customer returns HTTP 201.
2. Duplicate customer code returns HTTP 409.
3. Missing customer code returns HTTP 400.
4. Order with quantity <= 0 or negative unit price is rejected.
5. Order for a non-existent customer is rejected.
6. Empty data produces an empty RFM report.
7. K-means with fewer than 3 customers is rejected.
8. Wrong database settings produce a clear health-check failure.

## Submission checklist
Proposal/scope, database schema, Flask backend, RFM methodology, three chart images, test cases and results, README, limitations, screenshots, and an 8–12 minute demo.

## Limitations
Uses synthetic learning data. Rule labels depend on chosen thresholds; K-means results depend on sample size, scaling, and cluster count. Segments describe observed purchase patterns and do not prove customer intent or guarantee future behavior.
