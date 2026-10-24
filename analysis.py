from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
CHART_DIR = ROOT / "charts"
CHART_DIR.mkdir(exist_ok=True)

def build_rfm(customers, orders, items):
    c = pd.DataFrame(customers)
    o = pd.DataFrame(orders)
    i = pd.DataFrame(items)
    if c.empty:
        return pd.DataFrame(columns=["customer_id", "customer_code", "recency_days", "frequency", "monetary"])
    if o.empty or i.empty:
        r = c[["customer_id", "customer_code"]].copy()
        r["recency_days"], r["frequency"], r["monetary"] = 9999, 0, 0.0
        return r
    o["order_date"] = pd.to_datetime(o["order_date"], errors="coerce")
    o = o[o["order_status"].str.lower() == "completed"].copy()
    i["line_total"] = pd.to_numeric(i["quantity"]) * pd.to_numeric(i["unit_price"])
    joined = o.merge(i, on="order_id", how="inner")
    if joined.empty:
        r = c[["customer_id", "customer_code"]].copy()
        r["recency_days"], r["frequency"], r["monetary"] = 9999, 0, 0.0
        return r
    reference_date = joined["order_date"].max().normalize() + pd.Timedelta(days=1)
    a = joined.groupby("customer_id").agg(
        last_order=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("line_total", "sum")
    ).reset_index()
    a["recency_days"] = (reference_date - a["last_order"].dt.normalize()).dt.days
    r = c[["customer_id", "customer_code"]].merge(
        a[["customer_id", "recency_days", "frequency", "monetary"]],
        on="customer_id", how="left"
    )
    r["recency_days"] = r["recency_days"].fillna(9999).astype(int)
    r["frequency"] = r["frequency"].fillna(0).astype(int)
    r["monetary"] = r["monetary"].fillna(0).round(2)
    return r

def rule_segments(rfm):
    rfm = rfm.copy()
    def label(x):
        if x.frequency == 0: return "No Purchase Yet"
        if x.recency_days <= 30 and x.frequency >= 4 and x.monetary >= 1000: return "High-Value Active"
        if x.recency_days <= 60 and x.frequency >= 3: return "Loyal Customer"
        if x.recency_days > 90: return "At-Risk / Inactive"
        if x.frequency == 1: return "New / One-Time"
        return "Regular Customer"
    rfm["segment_label"] = rfm.apply(label, axis=1) if len(rfm) else pd.Series(dtype=str)
    return rfm

def kmeans_segments(rfm, n_clusters=3):
    if len(rfm) < 3:
        raise ValueError("K-means needs at least 3 customers.")
    if not 2 <= int(n_clusters) < len(rfm):
        raise ValueError("n_clusters must be >= 2 and less than the customer count.")
    x = rfm[["recency_days", "frequency", "monetary"]].astype(float).clip(lower=0)
    x = np.log1p(x)
    x = StandardScaler().fit_transform(x)
    model = KMeans(n_clusters=int(n_clusters), random_state=42, n_init=10)
    out = rfm.copy()
    out["cluster_id"] = model.fit_predict(x)
    out["segment_label"] = out["cluster_id"].map(lambda n: f"K-Means Cluster {n+1}")
    return out

def summary(rfm):
    if rfm.empty: return []
    s = rfm.groupby("segment_label").agg(
        customer_count=("customer_id", "count"),
        average_recency_days=("recency_days", "mean"),
        average_frequency=("frequency", "mean"),
        average_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum")
    ).reset_index().round(2)
    return s.replace({np.nan: None}).to_dict(orient="records")

def make_charts(rfm):
    if rfm.empty: return []
    outputs = []
    plots = [
        ("segment_distribution.png", rfm["segment_label"].value_counts(), "Customer Count by Segment", "Customer segment", "Number of customers"),
        ("average_spend_by_segment.png", rfm.groupby("segment_label")["monetary"].mean().sort_values(ascending=False), "Average Spend by Segment", "Customer segment", "Average spend (currency units)"),
        ("average_frequency_by_segment.png", rfm.groupby("segment_label")["frequency"].mean().sort_values(ascending=False), "Average Purchase Frequency by Segment", "Customer segment", "Average completed orders")
    ]
    for filename, values, title, xlabel, ylabel in plots:
        fig, ax = plt.subplots(figsize=(9, 5))
        values.plot(kind="bar", ax=ax)
        ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        fig.savefig(CHART_DIR / filename, dpi=140)
        plt.close(fig)
        outputs.append(f"charts/{filename}")
    return outputs
