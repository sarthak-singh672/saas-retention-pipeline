# read raw CSVs, clean, transform, save to processed

import pandas as pd
import numpy as np
import os

os.makedirs('processed', exist_ok=True)
print("B2B SaaS Retention Pipeline - ETL Starting...")

#--------------------------------------------------------------

# ACCOUNTS
print("\n[1/5] processing accounts...")

accounts = pd.read_csv('raw/ravenstack_accounts.csv')

# Fixing dates - convert signup_date from text to proper date
accounts['signup_date'] = pd.to_datetime(accounts['signup_date'])

# Clean plan_tier strip whitespace, make uppercase for consistency
accounts['plan_tier'] = accounts['plan_tier'].str.strip().str.upper()

# Clean industry and country - strip whitespace
accounts['industry'] = accounts['industry'].str.strip()
accounts['country'] = accounts['country'].str.strip()

# adding a calculated columns : how many days since signup?
accounts['days_since_signup'] = (pd.Timestamp.today()-accounts['signup_date']).dt.days

# Fill missing churn flag with 0 (asssuming not churned if unkown )
accounts['churn_flag'] = accounts['churn_flag'].fillna(0).astype(int)

# Fill missing is_trial with 0
accounts['is_trial'] = accounts['is_trial'].fillna(0).astype(int)

# Fill missing seats with median seats
accounts['seats'] = accounts['seats'].fillna(accounts['seats'].median()).astype(int)

print(f" Rows: {len(accounts)} | Nulls remaining: {accounts.isnull().sum().sum()}")
accounts.to_csv('processed/clean_accounts.csv', index=False)
print(" Saved: processed/clean_accounts.csv")

#---------------------------------------------------------------------

# SUBSCRIPTIONS
print("\n[2/5] Processing subscriptions...")

subs = pd.read_csv('raw/ravenstack_subscriptions.csv')

# Fix dates
subs['start_date'] = pd.to_datetime(subs['start_date'])
subs['end_date'] = pd.to_datetime(subs['end_date'])

# Add calculated column: subscription duration in days
subs['duration_days'] = (subs['end_date'] - subs['start_date']).dt.days

# Add calculated column: subscription duration in months (approx)
subs['duration_months'] = (subs['duration_days'] / 30).round(1)

# Clean plan_tier
subs['plan_tier'] = subs['plan_tier'].str.strip().str.upper()

# Fill missing mrr_amount with 0
subs['mrr_amount'] = subs['mrr_amount'].fillna(0)

# Fill missing arr_amount with 0
subs['arr_amount'] = subs['arr_amount'].fillna(0)

# Fill boolean flags with 0
for col in ['is_trial', 'upgrade_flag', 'downgrade_flag',
            'churn_flag', 'auto_renew_flag']:
    subs[col] = subs[col].fillna(0).astype(int)

# Add a label: what happened to this subscription?
def subscription_status(row):
    if row['churn_flag'] == 1:
        return 'CHURNED'
    elif row['upgrade_flag'] == 1:
        return 'UPGRADED'
    elif row['downgrade_flag'] == 1:
        return 'DOWNGRADED'
    else:
        return 'ACTIVE'

subs['subscription_status'] = subs.apply(subscription_status, axis=1)

print(f"  Rows: {len(subs)} | Nulls remaining: {subs.isnull().sum().sum()}")
print(f"  Status breakdown:\n{subs['subscription_status'].value_counts()}")
subs.to_csv('processed/clean_subscriptions.csv', index=False)
print("  Saved: processed/clean_subscriptions.csv ✓")

# ---------------------------------------------------------------------------

# SECTION 3: CHURN EVENTS
print("\n[3/5] Processing churn events...")

churn = pd.read_csv('raw/ravenstack_churn_events.csv')

# Fix dates
churn['churn_date'] = pd.to_datetime(churn['churn_date'])

# Add month and year columns — useful for cohort analysis later
churn['churn_month'] = churn['churn_date'].dt.month
churn['churn_year'] = churn['churn_date'].dt.year
churn['churn_month_label'] = churn['churn_date'].dt.to_period('M').astype(str)

# Clean reason_code
churn['reason_code'] = churn['reason_code'].str.strip()

# Fill missing refund amounts with 0
churn['refund_amount_usd'] = churn['refund_amount_usd'].fillna(0)

# Fill missing flags with 0
for col in ['preceding_upgrade_flag', 'preceding_downgrade_flag',
            'is_reactivation']:
    churn[col] = churn[col].fillna(0).astype(int)

# Categorize churn reason into broader groups
def categorize_churn_reason(reason):
    if pd.isna(reason):
        return 'UNKNOWN'
    reason = str(reason).upper()
    if any(word in reason for word in ['PRICE', 'COST', 'BUDGET', 'EXPENSIVE']):
        return 'PRICING'
    elif any(word in reason for word in ['FEATURE', 'PRODUCT', 'FUNCTION']):
        return 'PRODUCT'
    elif any(word in reason for word in ['SUPPORT', 'SERVICE', 'RESPONSE']):
        return 'SUPPORT'
    elif any(word in reason for word in ['COMPETITOR', 'ALTERNATIVE', 'SWITCH']):
        return 'COMPETITION'
    elif any(word in reason for word in ['CLOSE', 'SHUTDOWN', 'BANKRUPT']):
        return 'BUSINESS_CLOSED'
    else:
        return 'OTHER'

churn['churn_category'] = churn['reason_code'].apply(categorize_churn_reason)

print(f"  Rows: {len(churn)} | Nulls remaining: {churn.isnull().sum().sum()}")
print(f"  Churn categories:\n{churn['churn_category'].value_counts()}")
churn.to_csv('processed/clean_churn_events.csv', index=False)
print("  Saved: processed/clean_churn_events.csv ✓")


#-------------------------------------------------------------------------

# FEATURE USAGE
print("\n[4/5] Processing feature usage...")

usage = pd.read_csv('raw/ravenstack_feature_usage.csv')

# Fix dates
usage['usage_date'] = pd.to_datetime(usage['usage_date'])

# Add month label — for monthly usage trends
usage['usage_month'] = usage['usage_date'].dt.to_period('M').astype(str)

# Fill missing usage counts with 0
usage['usage_count'] = usage['usage_count'].fillna(0)
usage['usage_duration_secs'] = usage['usage_duration_secs'].fillna(0)
usage['error_count'] = usage['error_count'].fillna(0)

# Convert duration from seconds to minutes (easier to read)
usage['usage_duration_mins'] = (usage['usage_duration_secs'] / 60).round(2)

# Flag high error sessions (more than 5 errors = problematic session)
usage['is_high_error'] = (usage['error_count'] > 5).astype(int)

# Clean feature names
usage['feature_name'] = usage['feature_name'].str.strip()

# Fill boolean flag
usage['is_beta_feature'] = usage['is_beta_feature'].fillna(0).astype(int)

print(f"  Rows: {len(usage)} | Nulls remaining: {usage.isnull().sum().sum()}")
print(f"  Unique features: {usage['feature_name'].nunique()}")
usage.to_csv('processed/clean_feature_usage.csv', index=False)
print("  Saved: processed/clean_feature_usage.csv ✓")

#------------------------------------------------------------------------------

# SUPPORT TICKETS
print("\n[5/5] Processing support tickets...")

tickets = pd.read_csv('raw/ravenstack_support_tickets.csv')

# Fix dates
tickets['submitted_at'] = pd.to_datetime(tickets['submitted_at'])
tickets['closed_at'] = pd.to_datetime(tickets['closed_at'])

# Fill missing resolution time with median
tickets['resolution_time_hours'] = tickets['resolution_time_hours'].fillna(
    tickets['resolution_time_hours'].median()
)

# Fill missing first response time with median
tickets['first_response_time_minutes'] = tickets[
    'first_response_time_minutes'].fillna(
    tickets['first_response_time_minutes'].median()
)

# Fill missing satisfaction score with median
tickets['satisfaction_score'] = tickets['satisfaction_score'].fillna(
    tickets['satisfaction_score'].median()
)

# Fill escalation flag
tickets['escalation_flag'] = tickets['escalation_flag'].fillna(0).astype(int)

# Clean priority
tickets['priority'] = tickets['priority'].str.strip().str.upper()

# Add SLA breach flag: if resolution > 24 hours for HIGH priority
tickets['sla_breached'] = (
    (tickets['priority'] == 'HIGH') &
    (tickets['resolution_time_hours'] > 24)
).astype(int)

# Add satisfaction label
def satisfaction_label(score):
    if pd.isna(score):
        return 'UNKNOWN'
    elif score >= 4:
        return 'SATISFIED'
    elif score == 3:
        return 'NEUTRAL'
    else:
        return 'DISSATISFIED'

tickets['satisfaction_label'] = tickets['satisfaction_score'].apply(
    satisfaction_label
)

print(f"  Rows: {len(tickets)} | Nulls remaining: {tickets.isnull().sum().sum()}")
print(f"  SLA breaches: {tickets['sla_breached'].sum()}")
print(f"  Satisfaction:\n{tickets['satisfaction_label'].value_counts()}")
tickets.to_csv('processed/clean_support_tickets.csv', index=False)
print("  Saved: processed/clean_support_tickets.csv ✓")


# =============================================================
# FINAL SUMMARY
# =============================================================
print("\n" + "=" * 60)
print("ETL COMPLETE — Summary")
print("=" * 60)
print(f"  clean_accounts.csv        → {len(accounts)} rows")
print(f"  clean_subscriptions.csv   → {len(subs)} rows")
print(f"  clean_churn_events.csv    → {len(churn)} rows")
print(f"  clean_feature_usage.csv   → {len(usage)} rows")
print(f"  clean_support_tickets.csv → {len(tickets)} rows")
print("\nAll cleaned files saved to processed/ folder ✓")
print("Ready for PostgreSQL loading (Step 4)")










