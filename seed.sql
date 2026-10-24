USE customer_segmentation;

INSERT IGNORE INTO customers (customer_code, signup_date) VALUES
('CUST001','2025-01-10'),('CUST002','2025-02-15'),('CUST003','2025-03-20'),
('CUST004','2025-04-05'),('CUST005','2025-05-18'),('CUST006','2025-06-22'),
('CUST007','2025-07-12'),('CUST008','2025-08-09'),('CUST009','2025-09-14'),
('CUST010','2025-10-30'),('CUST011','2025-11-11'),('CUST012','2025-12-02');

-- Sample order inserts: intended to be run once on a fresh database.
INSERT INTO orders (customer_id, order_date, order_status)
SELECT customer_id,'2026-09-25','completed' FROM customers WHERE customer_code='CUST001';
SET @o1 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o1,2,750.00);
INSERT INTO orders (customer_id, order_date, order_status)
SELECT customer_id,'2026-10-05','completed' FROM customers WHERE customer_code='CUST001';
SET @o2 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o2,1,600.00);
INSERT INTO orders (customer_id, order_date, order_status)
SELECT customer_id,'2026-10-12','completed' FROM customers WHERE customer_code='CUST001';
SET @o3 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o3,2,800.00);
INSERT INTO orders (customer_id, order_date, order_status)
SELECT customer_id,'2026-10-18','completed' FROM customers WHERE customer_code='CUST001';
SET @o4 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o4,2,900.00);

INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-10-20','completed' FROM customers WHERE customer_code='CUST002';
SET @o5 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o5,1,350.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-07-12','completed' FROM customers WHERE customer_code='CUST003';
SET @o6 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o6,3,250.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-05-05','completed' FROM customers WHERE customer_code='CUST004';
SET @o7 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o7,1,1200.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-10-16','completed' FROM customers WHERE customer_code='CUST005';
SET @o8 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o8,2,400.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-08-22','completed' FROM customers WHERE customer_code='CUST006';
SET @o9 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o9,1,700.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-03-10','completed' FROM customers WHERE customer_code='CUST007';
SET @o10 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o10,1,180.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-10-19','completed' FROM customers WHERE customer_code='CUST008';
SET @o11 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o11,2,500.00);
INSERT INTO orders (customer_id,order_date,order_status)
SELECT customer_id,'2026-01-08','completed' FROM customers WHERE customer_code='CUST009';
SET @o12 = LAST_INSERT_ID();
INSERT INTO order_items (order_id,quantity,unit_price) VALUES (@o12,1,250.00);
