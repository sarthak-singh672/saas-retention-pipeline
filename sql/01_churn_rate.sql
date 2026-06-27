
-- Query 1: Churn Rate by Plan Tier
-- Business Question: Which plan tier has the highest churn?

SELECT
    a.plan_tier,
    COUNT(DISTINCT a.account_id)                    AS total_accounts,
    COUNT(DISTINCT ce.account_id)                   AS churned_accounts,
    ROUND(
        COUNT(DISTINCT ce.account_id) * 100.0 /
        COUNT(DISTINCT a.account_id), 2
    )                                               AS churn_rate_pct,
    COUNT(DISTINCT a.account_id) -
    COUNT(DISTINCT ce.account_id)                   AS retained_accounts
FROM accounts a
LEFT JOIN churn_events ce
    ON a.account_id = ce.account_id
GROUP BY a.plan_tier
ORDER BY churn_rate_pct DESC;