CREATE VIEW vw_sla_breaches AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    CASE
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
        ELSE 0
    END AS is_breach,
    EXTRACT(DAY FROM (
        o.order_delivered_customer_date - o.order_estimated_delivery_date
    )) AS days_late,
    oi.seller_id,
    oi.price,
    oi.freight_value,
    s.seller_state,
    COUNT(oi.order_item_id) OVER (PARTITION BY o.order_id) AS sku_count
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN sellers s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL;
