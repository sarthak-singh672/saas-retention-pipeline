
-- Query 2: Monthly Recurring Revenue (MRR) Trends
-- Business Question: How is revenue changing month by month?

SELECT
    TO_CHAR(s.start_date, 'YYYY-MM')               AS month,
    COUNT(DISTINCT s.account_id)                    AS active_accounts,
    ROUND(SUM(s.mrr_amount)::NUMERIC, 2)            AS total_mrr,
    ROUND(AVG(s.mrr_amount)::NUMERIC, 2)            AS avg_mrr_per_account,
    SUM(CASE WHEN s.upgrade_flag = 1
        THEN s.mrr_amount ELSE 0 END)               AS expansion_mrr,
    SUM(CASE WHEN s.churn_flag = 1
        THEN s.mrr_amount ELSE 0 END)               AS churned_mrr
FROM subscriptions s
GROUP BY TO_CHAR(s.start_date, 'YYYY-MM')
ORDER BY month;