
-- Query 3: Cohort Retention Analysis
-- Business Question: Of customers who signed up in month X,
-- how many are still active after N months?

WITH cohort_base AS (
    SELECT
        account_id,
        DATE_TRUNC('month', signup_date)            AS cohort_month
    FROM accounts
),
account_activity AS (
    SELECT
        s.account_id,
        DATE_TRUNC('month', s.start_date)           AS activity_month
    FROM subscriptions s
    WHERE s.churn_flag = 0
),
cohort_joined AS (
    SELECT
        cb.cohort_month,
        aa.activity_month,
        COUNT(DISTINCT cb.account_id)               AS active_accounts,
        EXTRACT(YEAR FROM AGE(
            aa.activity_month, cb.cohort_month
        )) * 12 +
        EXTRACT(MONTH FROM AGE(
            aa.activity_month, cb.cohort_month
        ))                                          AS months_since_signup
    FROM cohort_base cb
    JOIN account_activity aa
        ON cb.account_id = aa.account_id
    WHERE aa.activity_month >= cb.cohort_month
    GROUP BY cb.cohort_month, aa.activity_month
)
SELECT
    TO_CHAR(cohort_month, 'YYYY-MM')                AS cohort,
    months_since_signup,
    active_accounts
FROM cohort_joined
WHERE months_since_signup <= 12
ORDER BY cohort_month, months_since_signup;