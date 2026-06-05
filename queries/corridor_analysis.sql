-- Overall SLA breach summary
SELECT COUNT(*) AS total_records,
SUM(is_breach) AS total_breaches,
ROUND(100.0 * SUM(is_breach) / COUNT(*), 2) AS overall_breach_rate_pct
FROM vw_sla_breaches;

-- Corridor-level breach analysis
SELECT
    seller_state AS origin_state,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(is_breach) AS total_breaches,
    ROUND(100.0 * SUM(is_breach) / COUNT(DISTINCT order_id), 2) AS breach_rate_pct,
    ROUND(AVG(price), 2) AS avg_order_value,
    ROUND(SUM(CASE WHEN is_breach = 1 THEN price ELSE 0 END), 2) AS revenue_at_risk
FROM vw_sla_breaches
GROUP BY seller_state
ORDER BY breach_rate_pct DESC;

-- Cumulative breach concentration
WITH corridor_breaches AS (
    SELECT
        seller_state,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(is_breach) AS total_breaches,
        ROUND(100.0 * SUM(is_breach) / COUNT(DISTINCT order_id), 2) AS breach_rate_pct
    FROM vw_sla_breaches
    GROUP BY seller_state
),
totals AS (
    SELECT SUM(total_breaches) AS grand_total FROM corridor_breaches
)
SELECT
    seller_state,
    total_orders,
    total_breaches,
    breach_rate_pct,
    ROUND(100.0 * total_breaches / grand_total, 2) AS pct_of_total_breaches,
    ROUND(100.0 * SUM(total_breaches) OVER (ORDER BY total_breaches DESC) / grand_total, 2) AS cumulative_pct
FROM corridor_breaches, totals
ORDER BY total_breaches DESC;

-- Top 20 high risk carriers
SELECT
    seller_id,
    seller_state,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(is_breach) AS total_breaches,
    ROUND(100.0 * SUM(is_breach) / COUNT(DISTINCT order_id), 2) AS breach_rate_pct,
    ROUND(AVG(days_late) FILTER (WHERE is_breach = 1), 1) AS avg_days_late,
    ROUND(AVG(price), 2) AS avg_order_value
FROM vw_sla_breaches
GROUP BY seller_id, seller_state
HAVING COUNT(DISTINCT order_id) >= 50
ORDER BY breach_rate_pct DESC
LIMIT 20;
