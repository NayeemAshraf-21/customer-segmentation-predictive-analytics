CREATE DATABASE IF NOT EXISTS customer_segmentation
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE customer_segmentation;

CREATE TABLE IF NOT EXISTS customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_code VARCHAR(30) NOT NULL UNIQUE,
  signup_date DATE NULL
);

CREATE TABLE IF NOT EXISTS orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  order_date DATE NOT NULL,
  order_status VARCHAR(20) NOT NULL DEFAULT 'completed',
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
  INDEX idx_customer_order_date (customer_id, order_date)
);

CREATE TABLE IF NOT EXISTS order_items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
  CHECK (quantity > 0),
  CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS segment_runs (
  run_id INT AUTO_INCREMENT PRIMARY KEY,
  method VARCHAR(30) NOT NULL,
  run_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  parameters_json JSON NULL
);

CREATE TABLE IF NOT EXISTS customer_segments (
  run_id INT NOT NULL,
  customer_id INT NOT NULL,
  segment_label VARCHAR(60) NOT NULL,
  recency_days INT NOT NULL,
  frequency INT NOT NULL,
  monetary DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (run_id, customer_id),
  FOREIGN KEY (run_id) REFERENCES segment_runs(run_id) ON DELETE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
