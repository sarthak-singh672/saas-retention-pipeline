-- Query 5: At-Risk Customer Identification
-- Business Question: Which active customers show warning signs
-- of churning soon?


WITH usage_summary AS (
    SELECT
        s.account_id,
        COUNT(fu.usage_id)                          AS total_usage_events,
        AVG(fu.usage_count)                         AS avg_usage_count,
        SUM(fu.error_count)                         AS total_errors,
        MAX(fu.usage_date)                          AS last_usage_date
    FROM subscriptions s
    LEFT JOIN feature_usage fu
        ON s.subscription_id = fu.subscription_id
    GROUP BY s.account_id
),
ticket_summary AS (
    SELECT
        account_id,
        COUNT(ticket_id)                            AS total_tickets,
        AVG(satisfaction_score)                     AS avg_satisfaction,
        SUM(escalation_flag)                        AS escalations,
        SUM(sla_breached)                           AS sla_breaches
    FROM support_tickets
    GROUP BY account_id
),
risk_score AS (
    SELECT
        a.account_id,
        a.account_name,
        a.plan_tier,
        a.industry,
        COALESCE(us.total_usage_events, 0)          AS usage_events,
        COALESCE(us.total_errors, 0)                AS total_errors,
        COALESCE(ts.total_tickets, 0)               AS support_tickets,
        COALESCE(ts.avg_satisfaction, 5)            AS avg_satisfaction,
        COALESCE(ts.escalations, 0)                 AS escalations,
        COALESCE(ts.sla_breaches, 0)                AS sla_breaches,
        -- Risk scoring: higher = more at risk
        CASE WHEN COALESCE(us.total_usage_events,0)
            < 10 THEN 3 ELSE 0 END +
        CASE WHEN COALESCE(ts.avg_satisfaction, 5)
            < 3  THEN 3 ELSE 0 END +
        CASE WHEN COALESCE(ts.escalations, 0)
            > 2  THEN 2 ELSE 0 END +
        CASE WHEN COALESCE(us.total_errors, 0)
            > 50 THEN 2 ELSE 0 END +
        CASE WHEN COALESCE(ts.sla_breaches, 0)
            > 1  THEN 1 ELSE 0 END      AS risk_score
    FROM accounts a
    LEFT JOIN usage_summary us
        ON a.account_id = us.account_id
    LEFT JOIN ticket_summary ts
        ON a.account_id = ts.account_id
    WHERE a.churn_flag = 0
)
SELECT
    account_id,
    account_name,
    plan_tier,
    industry,
    usage_events,
    total_errors,
    support_tickets,
    ROUND(avg_satisfaction::NUMERIC, 2)             AS avg_satisfaction,
    escalations,
    sla_breaches,
    risk_score,
    CASE
        WHEN risk_score >= 7 THEN 'CRITICAL'
        WHEN risk_score >= 4 THEN 'HIGH'
        WHEN risk_score >= 2 THEN 'MEDIUM'
        ELSE 'LOW'
    END                                             AS risk_level
FROM risk_score
ORDER BY risk_score DESC
LIMIT 50;